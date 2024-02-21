Legenda

---------------------------------------------------------

Fine-tuning Llama-2-7B-chat on 761 couples (FOL, sentence), from dataset/train_refined.xlsx:

llama_2_ft_lora_fol.py


Inference (MATCHES and BERT-Score) with 100 unseen (FOL, sentence) from dataset/test_lkb3_gnd.xlsx:

llama_2_ft_bertscore_fol.py


Inference (MATCHES and BERT-Score) from dataset/test_lkb3_gnd.xlsx, with weights merged with base model:

llama_2_ft_bertscore_fol_merged.py


Fine-tuning Llama-2-7B-chat on 1000 Open qa couples (answer, response), from dolly dataset:

llama_2_ft_lora_dolly.py


Inference (MATCHES and BERT-Score) with 100 known couples (answer, response), from dolly dataset:

llama_2_ft_bertscore_fol.py


Inference (MATCHES and BERT-Score) with 100 known couples (answer, response) from dolly dataset, with weights merged with base model:

llama_2_ft_bertscore_fol_merged.py

Inference (MATCHES and BERT-Score) with 100 unseen (FOL, sentence) from dataset/test_lkb3_gnd.xlsx and with 100 known couples (answer, response) from dolly dataset, with combination (svd|linear|cat) of two adapters:


llama_2_ft_avg_qa_unified.py










