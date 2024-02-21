import spacy
import platform
import os
from collections import Counter
from nltk.corpus import wordnet
import configparser
import time
import re

# LLama
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer


config = configparser.ConfigParser()
config.read('config.ini')

GMC_ACTIVE = config.getboolean('GROUNDED_MEANING_CONTEXT', 'GMC_ACTIVE')
GMC_POS = config.get('GROUNDED_MEANING_CONTEXT', 'GMC_POS').split(", ")
OBJ_JJ_TO_NOUN = config.getboolean('POS', 'OBJ_JJ_TO_NOUN')

TEMP_FOL = float(config.get('LLM', 'TEMP_FOL'))
TEMP_QA = float(config.get('LLM', 'TEMP_QA'))
max_new_tokens = int(config.get('LLM', 'MAX_NEW_TOKENS'))
COMB_TYPE = config.get('LLM', 'COMB_TYPE')
WEIGHTS = config.get('LLM', 'WEIGHTS').split(", ")

base_model = config.get('LLM', 'BASE_MODEL')
adapter_name1 = config.get('LLM', 'ADAPTER_NAME1')
adapter_name2 = config.get('LLM', 'ADAPTER_NAME2')
adapter_path1 = config.get('LLM', 'ADAPTER_PATH1')
adapter_path2 = config.get('LLM', 'ADAPTER_PATH2')



class Parse(object):
    def __init__(self, VERBOSE):

        self.FILTER = ['det', 'punct', 'aux', 'auxpass', 'cc', 'case', 'intj', 'dep', 'predet', 'advcl']
        self.adv_adj_POS = ['RB', 'UH', 'RP', 'PRP', 'RBS', 'JJ', 'NN', 'RBR', 'DT']
        self.POS_FILTER = []
        self.VERBOSE = VERBOSE
        self.BLACK_LIST_WORDS = ['that', 'which', 'then']

        # nlp engine instantiation
        print("\nNLP engine initializing. Please wait...")

        # python -m spacy download en_core_web_trf
        self.nlp = spacy.load('en_core_web_trf')

        ##### Begin LLM Loading model section ###################

        w1 = float(WEIGHTS[0])  # fol
        w2 = float(WEIGHTS[1])  # dolly

        print(f"combination type: {COMB_TYPE}")
        print(f"weights: {w1}, {w2}")

        print(f"Starting to load the base model {base_model} and the combined adapters {adapter_name1}, {adapter_name2} into memory...")

        compute_dtype = getattr(torch, "float16")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=True,
        )
        self.model = AutoModelForCausalLM.from_pretrained(base_model, device_map={"": 0}, quantization_config=bnb_config)
        self.tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True)

        self.model = PeftModel.from_pretrained(self.model, adapter_path1, adapter_name="fol")
        self.model.load_adapter(adapter_path2, adapter_name="dolly")

        self.model.add_weighted_adapter(["fol", "dolly"], [w1, w2], combination_type=COMB_TYPE, adapter_name="dolly_fol")

        ##### End LLM Loading model section ###################

        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

        # enable cache usage
        self.FLUSH = True

        # last dependencies
        self.last_deps = []

        # last detected entities
        self.ner = []

        # last processed sentence
        self.last_sentence = None

        # last processed sentence
        self.pending_root_tense_debt = None

        # novel deps usage
        self.last_enc_deps = []

        # offset dictionary
        self.offset_dict = {}

        # Macro Semantic Table
        self.MST = [[], [], [], [], [], []]

        # GMC support dictionary
        self.GMC_SUPP = {}

        # GMC support dictionary reversed
        self.GMC_SUPP_REV = {}

        # Lemmas correction dictionary
        self.LCD = {}

        # Beginning Computational time
        self.start_time = 0



    def get_LLM(self, sub_prompt):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("\nGenerating llm text....\n")

        prompt = f"""### Instruction:
                    You are Joshua, an AI Assistant. Generate a response to the question given in Input.
                    ### Input:
                    {sub_prompt}

                    ### Response:
                    """
        input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True).input_ids.to(device)

        outputs = self.model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_p=0.9,
            temperature=TEMP_QA,
            pad_token_id=self.model.config.eos_token_id,
            attention_mask=torch.ones_like(input_ids)
        )

        gen_full = self.tokenizer.batch_decode(outputs.detach().cpu().numpy(), skip_special_tokens=True)[0][len(prompt):]
        # gen = gen_full.split("#")[0]
        #gen = gen.strip()

        ###################################################

        return gen_full


    def groundize(self, text):
        return re.sub(r'\(\w+\)', '', text)


    def get_LLM_from_fol(self, reasoning_result):

        pattern = r'[^:]+\)'
        matches = re.findall(pattern, reasoning_result)

        max_len = 0
        max_sottostringa = ""
        for match in matches:
            match = match.strip()
            if len(match) > max_len:
                max_len = len(match)
                max_sottostringa = match

        if len(max_sottostringa) > 5:

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            max_sottostringa = self.groundize(max_sottostringa)

            print("\nGenerating llm text from FOL....")
            print(f"subprompt: {max_sottostringa}\n")

            prompt = f"""### Instruction:
                                Use the Input below to create a sentence in expressive english, which could have been used to generate the Input logical form.
                                ### Input:
                                {max_sottostringa}

                                ### Response:
                                """

            input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True).input_ids.to(device)

            outputs = self.model.generate(
                input_ids=input_ids,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_p=0.9,
                temperature=TEMP_FOL,
                pad_token_id=self.model.config.eos_token_id,
                attention_mask=torch.ones_like(input_ids)
            )

            gen_full = self.tokenizer.batch_decode(outputs.detach().cpu().numpy(), skip_special_tokens=True)[0][
                       len(prompt):]
            gen = gen_full.split("#")[0]
            gen = gen.strip()

            return gen
        else:
            return "True"



    def set_start_time(self):
        self.start_time = time.time()


    def get_comp_time(self):
        assert_time = time.time() - self.start_time
        return assert_time


    def feed_MST(self, component, index):
        self.MST[index].append(component)


    def get_last_MST(self):
        return self.MST


    def get_pending_root_tense_debt(self):
        return self.pending_root_tense_debt

    def set_pending_root_tense_debt(self, d):
        self.pending_root_tense_debt = d

    def get_last_sentence(self):
        return self.last_sentence


    def get_last_ner(self):
        return self.ner


    def set_last_deps(self, deps):
        self.last_deps = deps


    def get_last_deps(self):
        return self.last_deps


    def get_flush(self):
        return self.FLUSH


    def flush(self):
        self.FLUSH = True
        self.last_deps = []
        self.ner = []
        self.MST = [[], [], [], [], [], []]


    def no_flush(self):
        self.FLUSH = False


    def get_nlp_engine(self):
        return self.nlp



    def get_pos(self, s):
        s_list = s.split(':')
        if len(s_list) > 1:
            return s_list[1]
        else:
            return s_list[0]


    def get_lemma(self, s):
        s_list = s.split('_')
        if len(s_list) == 1:
            result = s_list[0].split(":")[0]
        else:
            result = ""
            for i in range(len(s_list)):
                if i == 0:
                    result = s_list[i].split(':')[0]
                else:
                    result = result +"_"+s_list[i].split(':')[0]
        return result



    def get_deps(self, input_text, LEMMATIZED):

        nlp = self.get_nlp_engine()
        doc = nlp(input_text)
        self.last_sentence = input_text

        for X in doc.ents:
            ent = "("+X.label_ + ", " + X.text + ")"
            self.ner.append(ent)

        words_list = []
        for token in doc:
            words_list.append(token.text)

            enc_dep = []
            enc_dep.append(token.dep_)
            enc_dep.append(token.head.idx)
            enc_dep.append(token.idx)


        counter = Counter(words_list)

        offset_dict = {}
        offset_dict_lemmatized = {}


        for token in reversed(doc):
            index = counter[token.text]

            print("\nlemma in exam: ", token.lemma_)

            # check for presence in Grounded Meaning Context (GMC). In this case the choosen label must be that in GMC, already found
            if GMC_ACTIVE is True and token.tag_ in GMC_POS and token.lemma_ in self.GMC_SUPP:

                offset_dict[token.idx] = token.text[0].upper() + token.text[1:] + "0" + str(index) + ":" + token.tag_
                # offset_dict[token.idx] = token.text + "0" + str(index) + ":" + token.tag_
                shrinked_proper_syn = self.GMC_SUPP[token.lemma_]
                offset_dict_lemmatized[token.idx] = shrinked_proper_syn + "0" + str(index) + ":" + token.tag_

                print("\n<--------------- Getting from GMC: "+token.text+" ("+shrinked_proper_syn+")")

            else:

                lemma = str(token.lemma_).lower()

                # taking in account of possible past adj-obj corrections
                if OBJ_JJ_TO_NOUN is True and lemma in self.LCD:
                    lemma = self.LCD[lemma]
                    print("\n<------------- Getting from LCD: ", lemma)

                # offset_dict[token.idx] = token.text+"0"+str(index)+":"+token.tag_
                offset_dict[token.idx] = token.text[0].upper() + token.text[1:] + "0" + str(index) + ":" + token.tag_
                offset_dict_lemmatized[token.idx] = lemma+"0"+str(index)+":"+token.tag_

            counter[token.text] = index - 1

        deps = []
        for token in doc:
            new_triple = []
            new_triple.append(token.dep_)

            if token.head.lemma_ == '-PRON-':
                new_triple.append(offset_dict[token.head.idx])
            else:
                if LEMMATIZED:
                    new_triple.append(offset_dict_lemmatized[token.head.idx])
                else:
                    new_triple.append(offset_dict[token.head.idx])

            if token.lemma_ == '-PRON-':
                new_triple.append(offset_dict[token.idx])
            else:
                if LEMMATIZED:
                    new_triple.append(offset_dict_lemmatized[token.idx])
                else:
                    new_triple.append(offset_dict[token.idx])

            deps.append(new_triple)

        # query accomodation

        for d in deps:
            if d[2][0:5].lower() == "dummy":
                d[2] = "Dummy:DM"

        for i in range(len(deps)):
            governor = self.get_lemma(deps[i][1]).capitalize() + ":" + self.get_pos(deps[i][1])
            dependent = self.get_lemma(deps[i][2]).capitalize() + ":" + self.get_pos(deps[i][2])
            deps[i] = [deps[i][0], governor, dependent]

        return deps


    def morph(self, sent):
        sent_changed = ""
        for c in sent:
            if c in [':', '$', '.']:
                sent_changed = sent_changed + "_"
            else:
                sent_changed = sent_changed + c
        final_sent_changed = ""
        sent_changed_splitted = sent_changed.split(" ")
        for i in range(len(sent_changed_splitted)):
            if sent_changed_splitted[i][0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                if i == 0:
                    final_sent_changed = "N" + sent_changed_splitted[i]
                else:
                    final_sent_changed = final_sent_changed + " N" + sent_changed_splitted[i]
            else:
                if i == 0:
                    final_sent_changed = sent_changed_splitted[i]
                else:
                    final_sent_changed = final_sent_changed + " " + sent_changed_splitted[i]

        return final_sent_changed


    def shrink(self, word):
        chunk_list = word.split("_")
        sw = ""
        for chunk in chunk_list:
            sw = sw + chunk
        return sw


def main():

    # pos=VERB, NOUN, ADJ, ADV
    syns = wordnet.synsets("wise", pos=wordnet.ADJ, lang="eng")

    for synset in syns:

       print("\nsynset: ", synset.name())
       print("gloss: ", synset.definition())
       print("lemmas: ", synset.lemmas())
       for s in synset.examples():
           print("#synset example: ", s)


if __name__ == "__main__":
    main()








