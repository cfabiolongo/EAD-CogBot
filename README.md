# EAD-CogBot

This is the repository of the Python (3.10+) implementation of EAD-CogBot (Expressive Abductive-Deductive Cognitive ChatBot)
a framework able to instantiate chatbots for Abductive-Deductive reasoning on a first-order logic knowledge base, but endowed
of the expressive power of LLMs.

![Image 1](https://github.com/cfabiolongo/EAD-CogBot/blob/master/images/cogbot-arch.jpg)

# Installation

This repository has been tested with the following packages versions:

* [Phidias](https://github.com/corradosantoro/phidias) (release 1.3.4.alpha) 
* SpaCy (2.2.4)
* Natural Language Toolkit (3.5)
* python-telegram-bot (12.8)
* pymongo (3.10.1)
* pandas (2.1.4)


### Phidias

---------------

```sh
> git clone https://github.com/corradosantoro/phidias
> pip install -r requirements.txt
> pip install .
```

### SpaCy

---------------

```sh
> pip install spacy
> python -m spacy download en_core_web_trf
```


### Natural Language Toolkit

---------------

from prompt:
```sh
> pip install nltk
```
from python console:
```sh
> import nltk
> nltk.download('wordnet')
> nltk.download('omw-1.4')
```

### Telegram bot

---------------

```sh
> pip install python-telegram-bot==12.8
```


### pymongo

---------------

```sh
> pip install pymongo
```

### MongoDB

---------------
* Install a new Mongodb community instance from [here](https://www.mongodb.com/try/download/community) (a GUI Compass installation is also recommended from [here](https://www.mongodb.com/products/tools/compass)), then create a new database named *ad-caspar* containing a collection *clauses* (the easier way is by using Compass). The url of the MongoDB server must be specified by changing the value of HOST (section LKB) in config.ini.

* Create a new mongodb user in the Mongo shell (or Compass shell) as it follows:
```sh
> use ad-caspar
> db.createUser({
  user: "root",
  pwd: "example",
  roles: [
    { role: "readWrite", db: "ad-caspar" }
  ]
})
```


### MongoDB (Docker use case)

---------------
In the case of using a mongoDB container, the latter can be accessed by the link: http://localhost:8087/ (user/password are set in config.ini).

```sh
> docker-compose -f mongo.yaml up
```

### Pandas (for clauses exporting from mongodb to excel)


```sh
> pip install pandas
> pip install openpyxl
```

### Pytorch

Follow the instructions reported [here](https://pytorch.org/) for the current system.

### Llama 2 

* Download Llama-2-7b-chat-hf (or 70b) from [huggingface](
Llama-2-7b-chat-hf) andh copy it in a local folder. 

### QLoRA

```sh
> pip install transformers==4.34.0
> pip install peft==0.4.0
> pip install sentencepiece==0.1.99
> pip install datasets==2.13.0
> pip install accelerate==0.23.0
> pip install bitsandbytes==0.41.1
> pip install trl==0.4.7
> pip install safetensors>=0.3.1
> pip install scipy
```

### Huggingface hub (optional)
```sh
> pip install huggingface_hub
```


# Testing
Before going any further it is first necessary to create a new telegram bot by following the instruction
 in this [page](https://core.telegram.org/bots#6-botfather).  The returned token must be put in TELEGRAM_TOKEN (AGENT Section) in config.ini. 


### Starting Phidias Shell

---------------

```sh
> python ead-cogbot.py

          PHIDIAS Release 1.3.4.alpha (deepcopy-->clone,micropython,py3)
          Autonomous and Robotic Systems Laboratory
          Department of Mathematics and Informatics
          University of Catania, Italy (santoro@dmi.unict.it)
          
eShell: main >
```

### Setting interaction configuration

In section [LLM] of config.ini, the parameter *MODE* must be set as follows: 
* AD (Abduction-Deduction with FOL-to_NL response)
* LLM (only Query/Answer LLM)
* DUAL (AD+LLM) -----> to be added soon!

### Testing agent from shell (AD)

```sh
eShell: main > proc("Joe Biden is the President of United States.")

Asserting definite clause into Fol Kb.

 Is_VBZ(Joe_NNP_Biden_NNP(x1), Of_IN(President_NNP(x2), United_NNP_States_NNP(x3)))

```
### Inspecting High Knowledge Base
```sh
eShell: main > hkb()
Is_VBZ(Joe_NNP_Biden_NNP(x1), Of_IN(President_NNP(x2), United_NNP_States_NNP(x3)))

1 clauses in Higher Knowledge Base

```

### Query High Knowledge Base (AD) - *hot topic*
```sh
eShell: main > proc("Who is Joe Biden?")

Result: {v_27: x10, x11: Of_IN(President_NNP(v_28), United_NNP_States_NNP(v_29))}

Generating llm text from FOL....

The President of the United States
```

### Query High Knowledge Base (AD) - *non-hot topic*
```sh
eShell: main > proc("Who is Barack Obama?")

Generating llm text....

Well...I am not sure, but....Barack Obama is a former President of the United States.

```

### Starting chatbot

---------------

```sh
eShell: main > go()
EAD-CogBot started! Bot is running in AD mode...
```

### Inspecting Low Knowledge Base

In case of LKB_USAGE = true in [LKB] section of config.ini, Low Knowledge Base can be inspected as follows:

```sh
eShell: main > lkb()
0  clauses in Low Knowledge Base
eShell: main >
```

both High KB e Low KB can be emptied with the following commands:

```sh
eShell: main > chkb()
High Clauses kb initialized.
0  clauses deleted.
eShell: main > clkb()
Low Clauses kb initialized.
0  clauses deleted.
eShell: main >
```

to start a session you have to go to the telegram bot window and type the word "hello". 

![Image 2](https://github.com/cfabiolongo/EAD-CogBot/blob/master/images/waking.jpg){ width=50% }

Assertions must end with "." and questions must end with "?". 

![Image 3](https://github.com/cfabiolongo/EAD-CogBot/blob/master/images/hot-topic_assert.jpg)

After such interaction with the telegram bot, the two layers of the Clauses KB will be as it follows:

```sh
eShell: main > hkb()
eShell: main > Became_VBD(Barack_NNP_Obama_NNP(x1), Of_IN(President_NNP(x2), United_NNP_States_NNP(x3)))

1 clauses in High Knowledge Base

eShell: main > lkb()

Became_VBD(Barack_NNP_Obama_NNP(x1), Of_IN(President_NNP(x2), United_NNP_States_NNP(x3)))
['Became_VBD', 'Barack_NNP_Obama_NNP', 'Of_IN', 'President_NN', 'United_NNP_States_NNP']
Barack Obama became the president of United States.

1  clauses in Low Knowledge Base
```

Querying chatbot on hot topic...

![Image 4](https://github.com/cfabiolongo/EAD-CogBot/blob/master/images/hot-topic_questions.jpg)

Querying chatbot on non-hot topic wll let LLama-2-chat to get an answer from its implicit knowledge...

![Image 5](https://github.com/cfabiolongo/EAD-CogBot/blob/master/images/non-hot-topic_question.jpg)


### Automatic knowledge learning

This prototype gives the change to feed automatically the Clauses KB from file text, set with the parameter FILE_KB_NAME (AGENT section),
by the means of the command *feed()* given in the phidias prompt. 
Three examples knowledge base of increasing size are available for testing purposes: *west25.txt*, *west104.txt*, *west303.txt* (inside kbs folder). The command feed() must be executed after chatbot awakening with the word *hello* at startup.

```sh
> feed()
```

A syntax for a single input argument X is also available, for instance:

```sh
> feed("Colonel West is American")
```


### Exporting clauses into excel

This prototype gives the change to export Low Clauses KB content (clauses and corresponding sentences) into a excel file whose name must be
set in FILE_EXPORT_LKB_NAME (AGENT section), with the command *expt()* given in the phidias prompt. 

```sh
> expt()
```


### Querying the bot

A detailed overview of how the wh-questions are treated is provided [here](https://github.com/cfabiolongo/EAD-CogBot/blob/master/wquestions.md).
In case of LKB usage, after a bot reboot the result will be slightly different because the High Clauses KB
will be empty and must be populated getting clauses from the Low Clauses KB, taking in account of a confidence level about the presence of the lemmatized labels in the clauses.
Such a confidence level, depending of the domain can be changed by modifying the value of MIN_CONFIDENCE (LKB Section) in config.ini. The first query will get a result form the Low KB (From LKB: True), while the second one from the High KB (From HKB: True);
thats because the content of the High KB is preserved during the session, otherwise it can be emptied after a query by changing the value of
EMPTY_HKB_AFTER_REASONING (LKB Section) in config.ini.

### Nested Reasoning

In order to test the _Nested Reasoning_ you must be sure some parameters in config.ini are as it follows:

---------------

Section [NL_TO_FOL]:
* ASSIGN_RULES_ADMITTED = true
* CONDITIONAL_WORDS = WHEN

Section [REASONING]
* NESTED_REASONING = true

Section [GEN]
* GEN_PREP = true
* GEN_ADJ = true
* GEN_ADV = true

ASSIGN_RULES_ADMITTED ar used for creating logic implication starting from a copular verbs (*be*, present tense), while
CONDITIONAL_WORDS (*when*, *if*, *while*, etc.) are those for what we want a logic implication will be asserted.

### Known issues

It is well-known that natural language can be ambiguous, subject to interpretation about the semantic role of each lexical parts.
For such a reason out-of-common sense utterance might lead to unexpected logical forms, due to the dataset the dependency parser has been trained on. Still, as reported [here](https://spacy.io/usage/facts-figures), the model used for dependency parsing has an accuracy of 0.90 (optionally *en_core_web_trf* might be used, which has 0.95, but similarity is not supported so disambiguation won't work), which means that some missful/wrong dependecy classification is expected.
Beyond that, the following are known issues related to the code in this repository:

---------------

* Anaphora resolution/coreferentiators are not included yet in this code. So it is recommended to not use sentence containing pronoms, otherwise any abductive/deductive operations won't be successful.
For this purpose, the integration of tools such as [neuralcoref](https://github.com/huggingface/neuralcoref) is planned. Coders might include such a tool in their own fork of this repository.
* Sentence containing singles quoation marks (') are still not well managed. So, it is recommended to not use it, and, in such a case, to rephrase utterances differently.
* Occasional crashes during parsing of text may occur, especially during conversion from natural language into logical forms/definite clauses. In this case, rephrasing/reducing utterances is recommended.
* IMPORTANT: all production rules are designed starting from a toy domain. Practical use involves a global review of all parsing rules and modules.