#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="rag_papers"
mkdir -p "$OUT_DIR"

download() {
  url="$1"
  name="$2"
  out="/Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/data/RAG-survey/$name"
  if [ -f "$out" ]; then
    echo "Skip (exists): $name"
    return
  fi
  echo "Downloading: $name"
  curl -L "$url" -o "$out"
  sleep 1  # be polite
}

########################################
# Query-based RAG
########################################

download "https://arxiv.org/pdf/2002.08909.pdf" "REALM_2002.08909.pdf"
download "https://arxiv.org/pdf/2310.11511.pdf" "Self-RAG_2310.11511.pdf"
download "https://arxiv.org/pdf/2301.12652.pdf" "REPLUG_2301.12652.pdf"
download "https://arxiv.org/pdf/2302.00083.pdf" "In-Context-RAG_2302.00083.pdf"
download "https://arxiv.org/pdf/2210.17236.pdf" "When-LM-Meets-Private-Library_2210.17236.pdf"

download "https://openreview.net/pdf?id=ZTCxT2t2Ru" "DocPrompting.pdf"
download "https://doi.org/10.1109/ICSE48619.2023.00205" "Retrieval-based-prompt-selection-code-few-shot.pdf"
download "https://doi.org/10.1145/3611643.3613892" "InferFix.pdf"
download "https://proceedings.mlr.press/v202/huang23i/huang23i.pdf" "Make-an-audio_PMLR202.pdf"
download "https://doi.org/10.18653/v1/2022.acl-long.431" "ReACC_2022-acl-long-431.pdf"
download "https://doi.org/10.18653/v1/2022.emnlp-main.605" "Uni-Parser_2022-emnlp-main-605.pdf"
download "https://doi.org/10.18653/v1/2022.acl-long.417" "RNG-KBQA_2022-acl-long-417.pdf"
download "https://doi.org/10.18653/v1/2023.eacl-main.255" "End-to-end-case-based-reasoning-KB-completion.pdf"
download "https://arxiv.org/pdf/2311.08894.pdf" "Transfer+ICL-for-KBQA_2311.08894.pdf"
download "https://arxiv.org/pdf/2304.09667.pdf" "GeneGPT_2304.09667.pdf"
download "https://dl.acm.org/doi/pdf/10.1145/3584371.3612956" "RAG-Adolescent-Scoliosis-Shared-Decision-Making.pdf"
download "https://link.springer.com/content/pdf/10.1007/978-3-030-58598-3_15.pdf" "RetrieveGAN_ECCV-Chapter.pdf"
download "https://proceedings.neurips.cc/paper/2021/file/e7ac288b0f2d41445904d071ba37aaff-Paper.pdf" "Instance-conditioned-GAN_NeurIPS2021.pdf"
download "https://arxiv.org/pdf/2402.02972.pdf" "RAG-Score-Distillation-Text-to-3D_2402.02972.pdf"

########################################
# Latent Representation-based RAG
########################################

download "https://aclanthology.org/2021.eacl-main.74.pdf" "Leveraging-passage-retrieval-open-domain-QA_EACL2021.pdf"
download "https://doi.org/10.1109/ICSME55016.2022.00016" "BashExplainer-ICSME2022.pdf"
download "https://doi.org/10.1109/ASE51524.2021.9678724" "EditSum-ASE2021.pdf"
download "https://arxiv.org/pdf/2010.04459.pdf" "Retrieve-and-Refine-Comment-Generation_2010.04459.pdf"
download "https://doi.org/10.18653/v1/2022.emnlp-main.372" "RACE-Commit-Msg-Generation_EMNLP2022.pdf"
download "https://aclanthology.org/2022.findings-naacl.115.pdf" "Unik-QA_FindingsNAACL2022.pdf"
download "https://proceedings.neurips.cc/paper/2018/file/cd17d3ce3b64f227987cd92cd701cc58-Paper.pdf" "Retrieve-and-Edit-Structured-Outputs_NeurIPS2018.pdf"
download "https://openreview.net/pdf?id=XHc5zRPxqV9" "DecAF_OpenReview.pdf"
download "https://dl.acm.org/doi/pdf/10.1145/3583780.3615150" "Bridging-KB-Text-Gap-KBQA.pdf"
download "https://arxiv.org/pdf/2308.13259.pdf" "Knowledge-driven-CoT_2308.13259.pdf"
download "https://dl.acm.org/doi/pdf/10.1145/3539618.3592052" "Retrieval-enhanced-KG-completion.pdf"
download "https://aclanthology.org/2021.emnlp-main.755.pdf" "Case-based-reasoning-natural-language-KB-queries.pdf"
download "https://chemrxiv.org/engage/api-gateway/chemrxiv/article/6482d9dbbe16ad5c57af1937/content" "Protein-Ligand-3D-Generative-Framework_ChemRxiv.pdf"
download "https://proceedings.mlr.press/v162/borgeaud22a/borgeaud22a.pdf" "Improving-LMs-by-Retrieving-from-Trillions-of-Tokens_PMLR162.pdf"
download "https://doi.org/10.1109/ICCV51070.2023.00040" "ReMoDiffuse_ICCV2023.pdf"
download "https://openreview.net/pdf?id=TrjbxzRcnf-" "Memorizing-Transformers_OpenReview.pdf"
download "https://arxiv.org/pdf/2012.07331.pdf" "Audio-captioning-similar-caption-retrieval_2012.07331.pdf"
download "https://dl.acm.org/doi/pdf/10.1145/3539225" "RAG-Conv-Encoder-Decoder-Video-Captioning_ACM-MM.pdf"
download "https://arxiv.org/pdf/2401.00789.pdf" "RAG-Egocentric-Video-Captioning_2401.00789.pdf"
download "https://arxiv.org/pdf/2209.14491.pdf" "Re-imagen_2209.14491.pdf"
download "https://arxiv.org/pdf/2204.02849.pdf" "KNN-diffusion_2204.02849.pdf"
download "https://proceedings.neurips.cc/paper_files/paper/2022/file/62868cc2fc1eb5cdf321d05b4b88510c-Paper-Conference.pdf" "Retrieval-augmented-diffusion-models_NeurIPS2022.pdf"
download "https://arxiv.org/pdf/2207.13038.pdf" "Text-guided-artistic-images-RAG-diffusion_2207.13038.pdf"
download "https://arxiv.org/pdf/2208.07022.pdf" "Memory-driven-text-to-image_2208.07022.pdf"
download "https://arxiv.org/pdf/2110.06176.pdf" "Mention-Memory_2110.06176.pdf"
download "https://arxiv.org/pdf/2305.01625.pdf" "Unlimiformer_2305.01625.pdf"
download "https://arxiv.org/pdf/2004.07202.pdf" "Entities-as-Experts_2004.07202.pdf"
download "https://arxiv.org/pdf/2312.12763.pdf" "AMD-Anatomical-motion-diffusion_2312.12763.pdf"
download "https://arxiv.org/pdf/2309.08051.pdf" "RAG-Text-to-Audio_2309.08051.pdf"
download "https://doi.org/10.1109/TIP.2023.3307969" "Concept-aware-video-captioning_TIP2023.pdf"

########################################
# Logit-based RAG
########################################

download "https://openreview.net/pdf?id=HklBjCEKvH" "kNN-LM_OpenReview.pdf"
download "https://aclanthology.org/2023.findings-emnlp.90.pdf" "Syntax-aware-RAG-code-generation_FindingsEMNLP2023.pdf"
download "https://aaai.org/ojs/index.php/AAAI/article/view/20608/20367" "Memory-augmented-image-captioning_AAAI.pdf"
download "https://dl.acm.org/doi/pdf/10.1145/3377811.3380383" "Retrieval-based-neural-code-summarization.pdf"
download "https://aclanthology.org/2021.emnlp-main.461.pdf" "Efficient-kNN-LM_EMNLP2021.pdf"
download "https://aclanthology.org/2023.findings-acl.132.pdf" "Nonparametric-MLM_FindingsACL2023.pdf"
download "https://doi.org/10.1109/ASE51524.2021.9678724" "EditSum-Logit-RAG-duplicate-safe.pdf"

########################################
# Speculative RAG
########################################

download "https://arxiv.org/pdf/2311.08252.pdf" "REST_Retrieval-based-Speculative-Decoding_2311.08252.pdf"
# GPTCache is a repo, not a paper; you can git clone separately if needed
download "https://arxiv.org/pdf/2307.06962.pdf" "Copy-is-all-you-need_2307.06962.pdf"
download "https://arxiv.org/pdf/2402.17532.pdf" "Retrieval-is-Accurate-Generation_2402.17532.pdf"

########################################
# Input Enhancement – Query Transformations
########################################

download "https://aclanthology.org/2023.emnlp-main.585.pdf" "Query2doc_EMNLP2023.pdf"
download "https://openreview.net/pdf?id=vDvFT7IX4O" "Tree-of-Clarifications_OpenReview.pdf"
download "https://aclanthology.org/2023.acl-long.99.pdf" "Precise-zero-shot-dense-retrieval_ACL2023.pdf"
download "https://arxiv.org/pdf/2404.00610.pdf" "RQ-RAG_2404.00610.pdf"
download "https://arxiv.org/pdf/2403.11413.pdf" "Dynamic-contexts-RAG-conversation_2403.11413.pdf"

########################################
# Input Enhancement – Data Augmentation
########################################

download "https://arxiv.org/pdf/2402.04333.pdf" "LESS_2402.04333.pdf"
download "https://proceedings.mlr.press/v202/huang23i/huang23i.pdf" "Make-an-Audio-dup_PMLR202.pdf"
download "https://arxiv.org/pdf/2404.15939.pdf" "Telco-RAG_2404.15939.pdf"

########################################
# Retriever Enhancement – Recursive Retrieve
########################################

download "https://arxiv.org/pdf/2305.03653.pdf" "Query-Expansion-prompting-LLMs_2305.03653.pdf"
download "https://arxiv.org/pdf/2403.05313.pdf" "RAT_Retrieval-augmented-thoughts_2403.05313.pdf"
download "https://arxiv.org/pdf/2210.03629.pdf" "ReAct_2210.03629.pdf"
download "https://arxiv.org/pdf/2201.11903.pdf" "CoT_2201.11903.pdf"
download "https://aclanthology.org/2023.findings-emnlp.86.pdf" "LLMs-contextual-search-intent_FindingsEMNLP2023.pdf"
download "https://arxiv.org/pdf/2402.13547.pdf" "ActiveRAG_2402.13547.pdf"
download "https://arxiv.org/pdf/2402.07812.pdf" "RAG-as-Sequential-Decision-Making_2402.07812.pdf"
download "https://arxiv.org/pdf/2402.10790.pdf" "Recurrent-memory-finds-needles_2402.10790.pdf"
download "https://arxiv.org/pdf/2307.03172.pdf" "Lost-in-the-Middle_2307.03172.pdf"

########################################
# Retriever Enhancement – Chunk Optimization
########################################

# LlamaIndex is a repo; no paper download here
download "https://arxiv.org/pdf/2401.18059.pdf" "RAPTOR_2401.18059.pdf"
download "https://arxiv.org/pdf/2401.11246.pdf" "Prompt-RAG-Korean-Medicine_2401.11246.pdf"
download "https://arxiv.org/pdf/2405.12363.pdf" "Question-based-Retrieval-Atomic-Units_2405.12363.pdf"

########################################
# Retriever Enhancement – Finetune Retriever
########################################

download "https://arxiv.org/pdf/2309.07597.pdf" "C-Pack_2309.07597.pdf"
download "https://arxiv.org/pdf/2402.03216.pdf" "BGE-M3_2402.03216.pdf"
download "https://arxiv.org/pdf/2311.13534.pdf" "LM-Cocktail_2311.13534.pdf"
download "https://arxiv.org/pdf/2310.07554.pdf" "Retrieve-Anything_2310.07554.pdf"
download "https://arxiv.org/pdf/2301.12652.pdf" "REPLUG-dup_2301.12652.pdf"
download "https://doi.org/10.18653/v1/2022.findings-emnlp.21" "When-LM-meets-private-library_FindingsEMNLP2022.pdf"
download "https://doi.org/10.1109/ASE51524.2021.9678724" "EditSum-dup-ASE2021.pdf"
download "https://openreview.net/pdf?id=KmtVD97J43e" "Synchromesh_OpenReview.pdf"
download "https://dl.acm.org/doi/pdf/10.1145/3539225" "RAG-Conv-Encoder-Decoder-VideoCap-dup.pdf"
download "https://arxiv.org/pdf/2401.06800.pdf" "RL-Optimizing-RAG-Domain-Chatbots_2401.06800.pdf"

########################################
# Retriever Enhancement – Hybrid Retrieve
########################################

download "https://dl.acm.org/doi/pdf/10.1145/3611643.3616256" "RAP-Gen_Automatic-program-repair.pdf"
download "https://doi.org/10.18653/v1/2022.acl-long.431" "ReACC-dup_ACL2022.pdf"
download "https://dl.acm.org/doi/pdf/10.1145/3377811.3380383" "Retrieval-based-code-summarization-dup.pdf"
download "https://doi.org/10.1109/ICSME55016.2022.00016" "BashExplainer-dup.pdf"
download "https://arxiv.org/pdf/2402.02972.pdf" "RAG-Score-Distillation-Text-to-3D-dup_2402.02972.pdf"
download "https://arxiv.org/pdf/2401.15884.pdf" "Corrective-RAG_2401.15884.pdf"
download "https://aclanthology.org/2023.ijcnlp-main.65.pdf" "RAG-rich-answer-encoding_IJCNLP2023.pdf"
download "https://arxiv.org/pdf/2401.13256.pdf" "UniMS-RAG_2401.13256.pdf"
download "https://arxiv.org/pdf/2403.07222.pdf" "Sketch-text-duet-fine-grained-image-retrieval_2403.07222.pdf"
download "https://arxiv.org/pdf/2404.07220.pdf" "Blended-RAG_2404.07220.pdf"

########################################
# Retriever Enhancement – Re-ranking
########################################

download "https://aclanthology.org/2022.naacl-main.194.pdf" "Re2G_NAACL2022.pdf"
download "https://arxiv.org/pdf/1901.04085.pdf" "Passage-reranking-BERT_1901.04085.pdf"
download "https://arxiv.org/pdf/2303.17780.pdf" "AceCoder_2303.17780.pdf"
download "https://aclanthology.org/2022.findings-emnlp.384.pdf" "XRICL_FindingsEMNLP2022.pdf"
download "https://arxiv.org/pdf/2402.17081.pdf" "Fine-tuning-enhanced-RAG-Quantized-Influence-AI-judge_2402.17081.pdf"
download "https://arxiv.org/pdf/2303.00807.pdf" "UDAPDR_2303.00807.pdf"
download "https://arxiv.org/pdf/2307.07164.pdf" "Learning-to-retrieve-in-context-examples_2307.07164.pdf"
download "https://arxiv.org/pdf/2401.07883.pdf" "Chronicles-of-RAG_2401.07883.pdf"
download "https://arxiv.org/pdf/2403.10446.pdf" "Enhancing-LLM-factual-accuracy-RAG_2403.10446.pdf"

########################################
# Retrieval Transformation / Other Enhancements
########################################

download "https://arxiv.org/pdf/2311.08377.pdf" "Learning-to-filter-context-RAG_2311.08377.pdf"
download "https://arxiv.org/pdf/2209.14290.pdf" "FiD-light_2209.14290.pdf"
download "https://arxiv.org/pdf/2310.20158.pdf" "GAR-meets-RAG_2310.20158.pdf"
download "https://arxiv.org/pdf/2209.10063.pdf" "Generate-rather-than-retrieve_2209.10063.pdf"
download "https://arxiv.org/pdf/2307.11278.pdf" "Generator-Retriever-Generator_2307.11278.pdf"
download "https://arxiv.org/pdf/2406.05085.pdf" "Multi-Head-RAG_2406.05085.pdf"

########################################
# Prompt Engineering & Generator Enhancements
########################################

# Prompt Engineering Guide is a GitHub repo
download "https://arxiv.org/pdf/2310.06117.pdf" "Take-a-Step-Back_2310.06117.pdf"
download "https://arxiv.org/pdf/2302.12246.pdf" "Active-Prompting-CoT_2302.12246.pdf"
download "https://papers.nips.cc/paper_files/paper/2022/file/9d5609613524ecf4f15af0f7b31abca4-Paper-Conference.pdf" "CoT-NeurIPS2022.pdf"
download "https://aclanthology.org/2023.emnlp-main.825.pdf" "LLMLingua_EMNLP2023.pdf"
download "https://doi.org/10.48550/arXiv.2307.03172" "Lost-in-the-Middle-doi_2307.03172.pdf"
download "https://doi.org/10.1109/ICCV51070.2023.00040" "ReMoDiffuse-dup-ICCV2023.pdf"
download "https://arxiv.org/pdf/2304.06815.pdf" "Automatic-Semantic-Augmentation-Code-Summarization_2304.06815.pdf"
download "https://doi.org/10.1109/ICSE48619.2023.00205" "Retrieval-based-prompt-selection-dup.pdf"
download "https://doi.org/10.18653/v1/2022.findings-emnlp.384" "XRICL-dup.pdf"
download "https://proceedings.mlr.press/v202/huang23i/huang23i.pdf" "Make-An-Audio-dup2.pdf"

########################################
# Decoding Tuning / Finetune Generator (only a subset shown)
########################################

download "https://doi.org/10.1145/3611643.3613892" "InferFix-dup.pdf"
download "https://openreview.net/pdf?id=KmtVD97J43e" "Synchromesh-dup.pdf"
download "https://proceedings.mlr.press/v162/borgeaud22a/borgeaud22a.pdf" "Retrieving-from-trillions-dup.pdf"
download "https://doi.org/10.18653/v1/2022.findings-emnlp.21" "When-LM-Meets-Private-Library-dup2.pdf"
download "https://arxiv.org/pdf/2203.13474.pdf" "CodeGen_2203.13474.pdf"
download "https://doi.org/10.1109/TIP.2023.3307969" "Concept-aware-video-captioning-dup.pdf"
download "https://arxiv.org/pdf/2307.06940.pdf" "Animate-A-Story_2307.06940.pdf"
download "https://arxiv.org/pdf/2106.09685.pdf" "LoRA_2106.09685.pdf"
download "https://arxiv.org/pdf/2402.02972.pdf" "RAG-Score-Distillation-Text-to-3D-dup2.pdf"

########################################
# You can continue adding the rest of the long tail similarly if needed
########################################

########################################
# Others (De-fine, numerical reasoning, etc.)
########################################

download "https://arxiv.org/pdf/2311.12890.pdf" "De-fine_2311.12890.pdf"
download "https://arxiv.org/pdf/2305.18170.pdf" "Few-shot-prompting-numerical-reasoning_2305.18170.pdf"
download "https://arxiv.org/pdf/2311.02962.pdf" "RAG-CodeGen-Universal-IE_2311.02962.pdf"
download "https://arxiv.org/pdf/2312.08477.pdf" "E-and-V_Static-Analysis-Pseudocode_2312.08477.pdf"
download "https://arxiv.org/pdf/2311.18450.pdf" "StackSpot-AI-Contextualized-Coding-Assistant_2311.18450.pdf"
download "https://arxiv.org/pdf/2310.15657.pdf" "Unusual-text-inputs-mobile-crash-detection_2310.15657.pdf"

########################################
# RAG for Audio – Audio Generation
########################################

download "https://arxiv.org/pdf/2309.08051.pdf" "RAG-Text-to-Audio_2309.08051.pdf"
download "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10095969" "CLAP-Large-scale-contrastive-language-audio-pretraining_ICASSP2023.pdf"
download "https://proceedings.mlr.press/v202/huang23i/huang23i.pdf" "Make-an-Audio_PMLR202.pdf"

########################################
# RAG for Audio – Audio Captioning
########################################

download "https://arxiv.org/pdf/2309.09836.pdf" "RECAP_RAG-Audio-Captioning_2309.09836.pdf"
download "https://arxiv.org/pdf/2012.07331.pdf" "Audio-captioning-similar-caption-retrieval_2012.07331.pdf"
download "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10095969" "CLAP-dup-AudioCaption_ICASSP2023.pdf"
download "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7952132" "CNN-architectures-large-scale-audio-classification_ICASSP2017.pdf"
download "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10448504" "Natural-language-supervision-audio-representations_10448504.pdf"
download "https://arxiv.org/pdf/2309.12242.pdf" "Weakly-supervised-Audio-Captioning-text-only_2309.12242.pdf"
download "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10448115" "Training-Audio-Captioning-without-Audio_10448115.pdf"

########################################
# RAG for Image – Image Generation
########################################

download "https://arxiv.org/pdf/2007.08513.pdf" "RetrieveGAN_2007.08513.pdf"
download "https://arxiv.org/pdf/2109.05070.pdf" "Instance-conditioned-GAN_2109.05070.pdf"
download "https://arxiv.org/pdf/2208.07022.pdf" "Memory-driven-text-to-image_2208.07022.pdf"
download "https://arxiv.org/pdf/2209.14491.pdf" "Re-imagen_2209.14491.pdf"
download "https://arxiv.org/pdf/2204.02849.pdf" "KNN-Diffusion_2204.02849.pdf"
download "https://arxiv.org/pdf/2204.11824.pdf" "Retrieval-Augmented-Diffusion_2204.11824.pdf"
download "https://arxiv.org/pdf/2207.13038.pdf" "Text-guided-artistic-images-RAG-diffusion_2207.13038.pdf"
download "https://arxiv.org/pdf/2303.01000.pdf" "X-and-Fuse_T2I_2303.01000.pdf"
download "https://arxiv.org/pdf/2401.11708.pdf" "Mastering-T2I-Recaptioning-Planning-MultiModal-LLMs_2401.11708.pdf"

########################################
# RAG for Image – Image Captioning
########################################

download "https://aaai.org/ojs/index.php/AAAI/article/view/16220/16027" "Memory-augmented-image-captioning_AAAI2021.pdf"
download "https://www.sciencedirect.com/science/article/pii/S0950705120308595/pdfft" "Retrieval-enhanced-adversarial-image-paragraph-captioning.pdf"
download "https://arxiv.org/pdf/2207.13162.pdf" "RAG-Transformer-Image-Captioning_2207.13162.pdf"
download "https://arxiv.org/pdf/2302.08268.pdf" "RAG-image-captioning_2302.08268.pdf"
download "https://arxiv.org/pdf/2212.05221.pdf" "REVEAL-RAG-VL-pretraining-multimodal-memory_2212.05221.pdf"
download "https://arxiv.org/pdf/2209.15323.pdf" "SmallCap-lightweight-RAG-captioning_2209.15323.pdf"
download "https://www.mdpi.com/2072-4292/16/1/196/pdf" "Cross-modal-retrieval-remote-sensing-captioning_RemoteSensing2024.pdf"

########################################
# RAG for Image – Other Vision
########################################

download "https://ojs.aaai.org/index.php/AAAI/article/view/20215/19974" "GPT-3-few-shot-KB-VQA_AAAI2022.pdf"
download "https://aclanthology.org/2022.emnlp-main.772.pdf" "RAG-VQA-outside-knowledge_EMNLP2022.pdf"
download "https://doi.org/10.1162/tacl_a_00356" "Augmenting-transformers-KNN-composite-memory-TACL.pdf"
download "https://aclanthology.org/2021.acl-long.435.pdf" "MARIA-visual-experience-chatbot_ACL2021.pdf"
download "https://aclanthology.org/2022.acl-long.390.pdf" "NMT-phrase-level-universal-visual-repr_ACL2022.pdf"

########################################
# RAG for Video – Captioning
########################################

download "https://aclanthology.org/D18-1433.pdf" "Background-knowledge-video-description_EMNLP2018.pdf"
download "https://dl.acm.org/doi/pdf/10.1145/3539225" "RAG-Conv-EncDec-video-captioning_ACM-MM2022.pdf"
download "https://doi.org/10.1109/TIP.2023.3307969" "Concept-aware-video-captioning_TIP2023.pdf"
download "https://arxiv.org/pdf/2401.00789.pdf" "RAG-egocentric-video-captioning_2401.00789.pdf"

########################################
# RAG for Video – QA & Dialogue
########################################

download "https://doi.org/10.1109/TNNLS.2019.2938015" "Memory-augmented-DRNN-video-QA_TNNLS2019.pdf"
download "https://openaccess.thecvf.com/content/ICCV2023W/MMFM/papers/Pan_Retrieving-to-Answer_Zero-Shot_Video_Question_Answering_with_Frozen_Large_Language_ICCVW_2023_paper.pdf" "Retrieving-to-answer-zero-shot-video-QA_ICCVW2023.pdf"
download "https://aclanthology.org/2020.acl-main.730.pdf" "TVQA-plus_ACL2020.pdf"
download "https://aclanthology.org/2022.naacl-main.247.pdf" "VGNMN-video-grounded-dialogue_NAACL2022.pdf"

download "https://proceedings.neurips.cc/paper_files/paper/2022/file/381ceeae4a1feb1abc59c773f7e61839-Paper-Conference.pdf" "LMs-with-image-descriptors-few-shot-video-NeurIPS2022.pdf"
download "https://arxiv.org/pdf/2402.10828.pdf" "RAG-Driver_2402.10828.pdf"
download "https://arxiv.org/pdf/2307.06940.pdf" "Animate-A-Story_2307.06940.pdf"
download "https://doi.org/10.1109/ICCV48922.2021.00175" "Frozen-in-Time_video-image-retrieval_ICCV2021.pdf"

########################################
# RAG for 3D
########################################

download "https://doi.org/10.1109/ICCV51070.2023.00040" "ReMoDiffuse-3D-motion-ICCV2023.pdf"
download "https://arxiv.org/pdf/2312.12763.pdf" "AMD-motion-diffusion_2312.12763.pdf"
download "https://arxiv.org/pdf/2402.02972.pdf" "RAG-score-distillation-Text-to-3D_2402.02972.pdf"

########################################
# RAG for Knowledge – KBQA (subset, many already covered)
########################################

download "https://aclanthology.org/2021.acl-demo.39.pdf" "ReTraCk_KBQA_ACL-demo2021.pdf"
download "https://aclanthology.org/2021.findings-emnlp.50.pdf" "Unseen-entity-handling-KBQA_FindingsEMNLP2021.pdf"
download "https://aclanthology.org/2021.emnlp-main.755.pdf" "Case-based-KB-queries_EMNLP2021-dup.pdf"
download "https://aclanthology.org/2022.coling-1.145.pdf" "Logical-form-multitask-KBQA_COLING2022.pdf"
download "https://aclanthology.org/2022.emnlp-main.555.pdf" "TIARA_multi-grained-KBQA_EMNLP2022.pdf"
download "https://aclanthology.org/2023.acl-long.57.pdf" "FC-KBQA_ACL2023-long57.pdf"
download "https://aclanthology.org/2023.nlrse-1.7.pdf" "Knowledge-augmented-LM-prompting-zero-shot-KGQA_2023nlrse-1.7.pdf"
download "https://aclanthology.org/2023.nlrse-1.1.pdf" "KG-augmented-LMs-complex-QA_2023nlrse-1.1.pdf"
download "https://arxiv.org/pdf/2309.11206.pdf" "Retrieve-Rewrite-Answer-KGQA_2309.11206.pdf"
download "https://aclanthology.org/2024.eacl-srw.7.pdf" "Distribution-shifts-grounding-LMs-KB_EACL-SRW2024.pdf"
download "https://arxiv.org/pdf/2401.05777.pdf" "Probing-structured-semantics-QA_2401.05777.pdf"
download "https://arxiv.org/pdf/2401.00426.pdf" "Keqing-KBQA-CoT-mentor_2401.00426.pdf"
download "https://arxiv.org/pdf/2402.15131.pdf" "Interactive-KBQA-multi-turn-LLMs_2402.15131.pdf"

########################################
# Benchmark (RAG)
########################################

download "https://arxiv.org/pdf/2309.01431.pdf" "Benchmarking-LLMs-in-RAG_2309.01431.pdf"
download "https://arxiv.org/pdf/2401.17043.pdf" "CRUD-RAG-Chinese-benchmark_2401.17043.pdf"
download "https://arxiv.org/pdf/2311.09476.pdf" "ARES_2311.09476.pdf"
download "https://arxiv.org/pdf/2309.15217.pdf" "RAGAS_2309.15217.pdf"
download "https://arxiv.org/pdf/2009.02252.pdf" "KILT_2009.02252.pdf"

echo "All downloads attempted. Files are in: $OUT_DIR"
