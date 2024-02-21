# AD-CASPAR

This is the repository of the Python (3.7+) implementation of AD-CASPAR (Abductive-Deductive Cognitive Architecture System Planned and Reactive)
referred to the short paper [AD-CASPAR: Abductive-Deductive Cognitive Architecture based on Natural Language and First Order Logic Reasoning](http://ceur-ws.org/Vol-2735/), presented in 
the 4th Workshop on Natural Language for Artificial Intelligence (NL4AI 2020) co-located with the 19th International Conference of the Italian Association for Artificial Intelligence (AI*IA 2020).
A full paper of the work is also available in [Cognitive Systems Research](https://www.sciencedirect.com/science/article/abs/pii/S1389041723000359). 
This architecture inherits all the features of his predecessor [CASPAR](https://github.com/fabiuslongo/pycaspar), extending them with a 
 two-level Clauses Knowledge Base, an abductive inference as pre-phase of deduction, and a Telegram
chatbot prototype implementing Question Answering tecniques for Polar and Wh-Questions. Such chatbot can have both goal-oriented and conversational features.

![Image 1](https://github.com/fabiuslongo/ad-caspar/blob/master/images/AD-Caspar.jpg)

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
> python ad-caspar.py

          PHIDIAS Release 1.3.4.alpha (deepcopy-->clone,micropython,py3)
          Autonomous and Robotic Systems Laboratory
          Department of Mathematics and Informatics
          University of Catania, Italy (santoro@dmi.unict.it)
          
eShell: main >
```
### Starting agent

---------------

```sh
eShell: main > go()
eShell: main > AD-Caspar started! Bot is running...
```

### Inspecting Knowledge Bases

---------------

After the agent is started, the Belief KB can be inspected with the following command:

```sh
eShell: main > kb
WAIT(1000)
eShell: main >
```
The value inside the belief WAIT represents the maximum duration of each session in seconds. It can be changed by modifying the value
of the variable WAIT_TIME (AGENT Section) in config.ini. The two layers of the Clauses KB (respectively High KB and Low KB) can be inspected with the following commands:

```sh
eShell: main > hkb()
0 clauses in High Knowledge Base
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

to start a session you have to go to the telegram bot window and type the word "hello". Assertions must end with 
"." and questions must end with "?". Otherwise the utterances will be processed as direct commands or routines (check out the page of [CASPAR](https://github.com/fabiuslongo/pycaspar) for details).

![Image 2](https://github.com/fabiuslongo/ad-caspar/blob/master/images/start-assertion.JPG)

After such interaction with the telegram bot, the two layers of the Clauses KB will be as it follows:

```sh
eShell: main > hkb()
eShell: main > In_IN(Become_VBD(Barack_NNP_Obama_NNP(x1), Of_IN(President_NN(x2), United_NNP_States_NNP(x3))), N2009_CD(x4))

1 clauses in High Knowledge Base

eShell: main > lkb()

In_IN(Become_VBD(Barack_NNP_Obama_NNP(x1), Of_IN(President_NN(x2), United_NNP_States_NNP(x3))), N2009_CD(x4))
['In_IN', 'Become_VBD', 'Barack_NNP_Obama_NNP', 'Of_IN', 'President_NN', 'United_NNP_States_NNP', 'N2009_CD']
Barack Obama became the president of United States in 2009.

1  clauses in Low Knowledge Base
```

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

A detailed overview of how the wh-questions are treated is provided [here](https://github.com/fabiuslongo/ad-caspar/blob/master/wquestions.md).
In the following picture are shown two different kind of query with wh-questions: 

![Image 3](https://github.com/fabiuslongo/ad-caspar/blob/master/images/query1.JPG)

This prototype give back as result a substitutions containing the literal as
logical representation of the snipplet-result of the query. After a bot reboot, as we can see in the following picture, the result will be slightly different because the High Clauses KB
will be empty and must be populated getting clauses from the Low Clauses KB, taking in account of a confidence level about the presence of the lemmatized labels in the clauses.
Such a confidence level, depending of the domain can be changed by modifying the value of MIN_CONFIDENCE (LKB Section) in config.ini. The first query will get a result form the Low KB (From LKB: True), while the second one from the High KB (From HKB: True);
thats because the content of the High KB is preserved during the session, otherwise it can be emptied after a query by changing the value of
EMPTY_HKB_AFTER_REASONING (LKB Section) in config.ini.

![Image 4](https://github.com/fabiuslongo/ad-caspar/blob/master/images/query2.JPG)

By changing the values of SHOW_REL (QA Section) in config.ini, it can be possible to show the clauses involved in the abduction pre-inference, together with their confidences.

![Image 5](https://github.com/fabiuslongo/ad-caspar/blob/master/images/query3.JPG)

### Failing queries

In the bot closed world assumption, the agent can give back only answers related to its onw knowledge, otherwise it will return _False_.
Optionally, with the value of SHOW_REL set to _true_, the closest results can be shown together with their confidence level: 

![Image 5](https://github.com/fabiuslongo/ad-caspar/blob/master/images/query4.JPG)

### Nested Reasoning

In order to test the _Nested Reasoning_ inherited from [CASPAR](https://github.com/fabiuslongo/pycaspar) by using the Telegram bot, you must be sure some parameters in config.ini are as it follows:

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

#### populating the knowledge base...

![Image 6](https://github.com/fabiuslongo/ad-caspar/blob/master/images/nested1.JPG)

![Image 7](https://github.com/fabiuslongo/ad-caspar/blob/master/images/nested2.JPG)

#### querying the knowledge base...

![Image 8](https://github.com/fabiuslongo/ad-caspar/blob/master/images/nested3.JPG)

#### querying the knowledge base after a reboot...

![Image 9](https://github.com/fabiuslongo/ad-caspar/blob/master/images/nested4.JPG)

After a failed attempt using the High KB (From HKB: False), a successful reasoning is achieved (From LKB: True) getting query-relevant clauses from the Low KB with a MIN_CONFIDENCE (Section [LKB] of config.ini) greater than 0.6.

### Assertion/Inference via shell (outside chatbot)

The response after assertion/reasoning commands can be simulated outside the chatbot, with the shell command *proc* as follow:

* Assertions (with final sentence dot)

```sh
> proc("Colonel West is American.")
```

* Questions (with final sentence question mark)

```sh
> proc("Colonel West is American?")
```

* IoT commands (with nothing at the end of sentence)

```sh
> proc("turn off the lights in the living room")
```



### Known issues

It is well-known that natural language can be ambiguous, subject to interpretation about the semantic role of each lexical parts.
For such a reason out-of-common sense utterance might lead to unexpected logical forms, due to the dataset the dependency parser has been trained on. Still, as reported [here](https://spacy.io/usage/facts-figures), the model used for dependency parsing has an accuracy of 0.90 (optionally *en_core_web_trf* might be used, which has 0.95, but similarity is not supported so disambiguation won't work), which means that some missful/wrong dependecy classification is expected.
Beyond that, the following are known issues related to the code in this repository:

---------------

* Anaphora resolution/coreferentiators are not included yet in this code. So it is recommended to not use sentence containing pronoms, otherwise any abductive/deductive operations won't be successful.
For this purpose, the integration of tools such as [neuralcoref](https://github.com/huggingface/neuralcoref) is planned. Coders might include such a tool in their own fork of this repository.
* Sentence containing singles quoation marks (') are still not well managed. So, it is recommended to not use it, and, in such a case, to rephrase utterances differently.
* Occasional crashes during parsing of text may occur, especially during conversion from natural language into logical forms/definite clauses. In this case, rephrasing/reducing utterances is recommended.
* Sometime disambiguation might not work well, due to possible lack of useful examples within related wordnet synsets that must be evaluated. It is planned to integrate additional lexical resources in order to address such an issue.
