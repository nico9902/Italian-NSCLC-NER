# Import libraries
import json
import re
import pickle
import numpy as np
from collections import Counter
from dateutil.parser import parse

# funtion that replace text with a number 
# of spaces equal to the length of the text
def replace_with_spaces(match):
    return " " * len(match.group())

# function that remove from the text the
# non-narrative part and the clinical non relevant-information
def text_pre(chars):
    chars = re.sub('\f', ' ', chars)
    regex = r"(?<=\s)FG(?=\s)"
    chars = re.sub(regex, '  ', chars)
    regex = r"(?<=\s)ADD(?=\s)"
    chars = re.sub(regex, '   ', chars)
    regex = r"(?<=\s)SP(?=\s)"
    chars = re.sub(regex, '  ', chars)
    regex = r"(?<=\s)SG(?=\s)"
    chars = re.sub(regex, '  ', chars)
    regex = r"(?<=\s)CG(?=\s)"
    chars = re.sub(regex, '  ', chars)
    regex = r"(?<=\s)GF(?=\s)"
    chars = re.sub(regex, '  ', chars)
    regex = r"(?<=\s)AC(?=\s)"
    chars = re.sub(regex, '  ', chars)
    regex = r"(?<=\s)IR(?=\s)"
    chars = re.sub(regex, '  ', chars)
    regex = r"(?<=\s)TRIGORIA(?=\s)"
    chars = re.sub(regex, replace_with_spaces, chars)
    #regex_rad = r"Radioterapia Trigoria.*?Firmato digitalmente da:.*?Tel\. \(\+39\) 06\.22541\.1 Fax \(\+39\) 06\.22541\.456 - www\.policlinicocampusbiomedico\.it"
    #regex_onc = r"Oncologia.*?Firmato digitalmente da:.*?Tel\. \(\+39\) 06\.22541\.1 Fax \(\+39\) 06\.22541\.456 - www\.policlinicocampusbiomedico\.it"
    regex_rad = r"Radioterapia Trigoria.*?Firmato digitalmente da:.*?Tel\. \(\+39\) 06\.22541\.1 Fax \(\+39\) 06\.22541\.456 - www\.policlinicocampusbiomedico\.it\s*((\d+)\s*\/\s*\d+)?"
    chars = re.sub(regex_rad, replace_with_spaces, chars)
    regex_onc = r"Oncologia.*?Firmato digitalmente da:.*?Tel\. \(\+39\) 06\.22541\.1 Fax \(\+39\) 06\.22541\.456 - www\.policlinicocampusbiomedico\.it\s*((\d+)\s*\/\s*\d+)?"
    chars = re.sub(regex_onc, replace_with_spaces, chars)
    regex_email = r"\w+\.?\w+@unicampus\.it"
    chars = re.sub(regex_email, replace_with_spaces, chars)
    regex_portillo = r"Via Àlvaro del Portillo, \d{3} – \d{5} Roma  Tel \(\+39\) \d{2}\.\d{2}\.\d{3}\.\d{4}\/\d{4} Fax \(\+39\) \d{2}\.\d{2}\.\d{3}\.\d{4}"
    chars = re.sub(regex_portillo, replace_with_spaces, chars)
    regex_sito = r"CF \d{11} - P\.I\.\d{11}  - Sito Internet: www\.policlinicocampusbiomedico\.it"
    chars = re.sub(regex_sito, replace_with_spaces, chars)
    regex_campus = r"Università Campus Bio-Medico di Roma"
    chars = re.sub(regex_campus, replace_with_spaces, chars)
    regex_seg = r"segreteria oncologica: \d{11}"
    chars = re.sub(regex_seg, replace_with_spaces, chars)
    # Rimuovere la parte finale del referto clinico
    regex = r'\n\n(Il medico responsabile).*'
    chars = re.sub(regex, replace_with_spaces, chars)
    regex = r'\n\n(grading medico).*'
    chars = re.sub(regex, replace_with_spaces, chars)
    regex = r'(Sede tossicitàGradingMedico).*'
    chars = re.sub(regex, replace_with_spaces, chars)
    regex = r'\n\n(Il radioterapista oncologo).*'
    chars = re.sub(regex, replace_with_spaces, chars)
    regex = r'\n\n(medico:).*'
    chars = re.sub(regex, replace_with_spaces, chars)
    regex = r'\n\n(Contatti:).*'
    chars = re.sub(regex, replace_with_spaces, chars)
    # Rimuovere le espressioni che si trovano tra le pagine
    regex = r'Via alvaro del portillo.*?www\.policlinicocampusbiomedico\.it'
    chars = re.sub(regex, replace_with_spaces, chars)

    # Identificare la sezione corretta (Notizie cliniche o Storia clinica oncologica)
    match = re.search(r'(Notizie cliniche|Storia clinica oncologica|VISITA DI OSTEO-ONCOLOGIA PER PIANFICIAZIONE TERAPEUTICA|VISITA DI CONTROLLO E PRESCRIZIONE FARMACI \[ONCOLOGIA\]|CONSULENZA RADIOTERAPICAT|VISITA SPECIALISTICA ONCOLOGICA DI CONTROLLO|VISITA DI RIVALUTAZIONE [RADIOTERAPIA ONCOLOGICAT]|VISITA SPECIALISTICA ONCOLOGICA|Referto di visita|Referto di Prima Visita|VISITE OSTEO-ONCOLOGICA DI CONTROLLO \(FOLLOW-UP\)|VISITA DI RIVALUTAZIONE \[RADIOTERAPIA ONCOLOGICA\]T)', chars)
    #section = match.group()
    if match is None:
        match = re.search(r'Visita radioterapicaT-Radioterapia|Referto ambulatoriale-Oncologia|I visita|I Visita|VISITA CLINICA \[RADIOTERAPIA ONCOLOGICA\]|CHEMIOTERAPIA ONCOLOGICA AMB \[ONCOLOGIA\]|Valutazione in ingresso|Prima visita|PRIMA VISITA|Visita di controllo|Visita radioterapicaT-Radioterapia TRIGORIA|Anamnesi fisiologica|Visita specialistica|Visita oncologica-Oncologia|CHEMIOTERAPIA ONCOLOGICA AMB \[ONCOLOGIA\]', chars)

    if match is not None:
        # Determinare la posizione del primo carattere dopo la sezione corretta
        start_pos = match.end()
        while start_pos < len(chars) and chars[start_pos].isspace():
            start_pos += 1

        # Estrarre il testo a partire dalla posizione determinata e fino alla fine del file
        text = chars[start_pos:]

        # Rimuovere le informazioni di fine pagina che contengono il nome del dottore e del paziente
        #pattern = re.compile(r'\n\n\nFirma.*?\n\n', re.DOTALL)
        #text = re.sub(pattern, '', text)

        return text, start_pos
    else:
        return None, None

# function to tokenize sequence
def get_words(chars):
    words_list = []
    word = ""
    separators = [" ", "(", ")", "\n", ".", ",", "\"", ":", ";", "*", "-", "=", "/", "X", "'"]
    matches = [":", "/"]

    for c in chars:
        if c in separators:
            if len(word) != 0 and any(x in word for x in matches):
                words_list.append(word) 
                words_list.append(c)
                word = ""
                c = ""
                continue
            
            # if (not word.islower() and not word.isupper() and not bool(re.search('\d', word))) and ("-" and ":") not in word:   # uppercase/lowercase handling
            elif (not word.islower() and not word.isupper() and not bool(re.search('\d', word))) and len(word) > 3:   # uppercase/lowercase handling
        
                if sum(map(str.islower, word)) == 1 and word[0].isupper() and word[-1].islower():    # handles            
                    word_upper = re.findall('[A-Z]+', word)
                    word_lower = re.findall('[a-z]+', word)
                    if len(words_list) != 0:
                        words_list.extend(word_upper)
                        words_list.extend(word_lower)
                    else:
                        for upper in word_upper:
                            words_list.append(upper)
                        for lower in word_lower:
                            words_list.append(lower)
                    
                    words_list.append(c)
                    word = ""
                    c = ""
                    continue

                elif sum(map(str.isupper, word)) == 1 and word[0].islower() and word[-1].isupper(): # handles "oncologicaT"
                    word_upper = re.findall('[A-Z]+', word)
                    word_lower = re.findall('[a-z]+', word)
                    if len(words_list) != 0:
                        words_list.extend(word_lower)
                        words_list.extend(word_upper)
                    else:
                        for lower in word_lower:
                            words_list.append(lower)
                        for upper in word_upper:
                            words_list.append(upper)
                    words_list.append(c)
                    word = ""
                    c = ""
                    continue
                
                # elif len(re.findall('[A-Z]+', word)[0]) > 1: # handles "BPCOsevera"
                elif len(re.findall('[A-Z]+', word)) != 0: # handles "BPCOsevera"
    
                    if len(re.findall('[A-Z]+', word)[0]) > 1:
                        word_lower = re.findall('[a-z]+', word)
                        word_upper = re.findall('[A-Z]+', word)
                        if word[0].islower():
                            for lower in word_lower:
                                words_list.append(lower)
                            for upper in word_upper:
                                words_list.append(upper)
                            words_list.append(c)
                            word = ""
                            c = ""
                            continue
                        else:
                            for upper in word_upper:
                                words_list.append(upper)
                            for lower in word_lower:
                                words_list.append(lower)
                            words_list.append(c)
                            word = ""
                            c = ""
                            continue
                
                word = re.findall('.[^A-Z]*', word)   # handles "DiagnosiCancroStadio > Diagnosi Cancro Stadio"
                words_list.extend(word)
                words_list.append(c)
                word = ""
                c = ""
                continue
            
            if word == "":
                words_list.append(c)
                continue

            if not (c == "X" and word.isdigit()==False):
                words_list.append(word) 
                words_list.append(c)
                word = ""
                c = ""
                continue           
        
        word += c

    check = False
    # Handle last word of the input chars
    if len(word) != 0:
        if (not word.islower() and not word.isupper() and not bool(re.search('\d', word))) and len(word) > 3:   # uppercase/lowercase handling
        
            if sum(map(str.islower, word)) == 1 and word[0].isupper() and word[-1].islower():    # handles            
                word_upper = re.findall('[A-Z]+', word)
                word_lower = re.findall('[a-z]+', word)
                if len(words_list) != 0:
                    words_list.extend(word_upper)
                    words_list.extend(word_lower)
                else:
                    for upper in word_upper:
                        words_list.append(upper)
                    for lower in word_lower:
                        words_list.append(lower)
                check = True

            elif sum(map(str.isupper, word)) == 1 and word[0].islower() and word[-1].isupper(): # handles "oncologicaT"
                
                word_upper = re.findall('[A-Z]+', word)
                word_lower = re.findall('[a-z]+', word)
                if len(words_list) != 0:
                    words_list.extend(word_lower)
                    words_list.extend(word_upper)
                else:
                    for lower in word_lower:
                        words_list.append(lower)
                    for upper in word_upper:
                        words_list.append(upper)
                check = True
            elif len(re.findall('[A-Z]+', word)) != 0: # handles "BPCOsevera"

                if len(re.findall('[A-Z]+', word)[0]) > 1:
                    word_lower = re.findall('[a-z]+', word)
                    word_upper = re.findall('[A-Z]+', word)
                    if word[0].islower():
                        for lower in word_lower:
                            words_list.append(lower)
                        for upper in word_upper:
                            words_list.append(upper)
                    else:
                        for upper in word_upper:
                            words_list.append(upper)
                        for lower in word_lower:
                            words_list.append(lower)
                    check = True
                #word = re.findall('.[^A-Z]*', word)   # handles "DiagnosiCancroStadio > Diagnosi Cancro Stadio"
                #words_list.extend(word)
        if check == False:
            words_list.append(word)

    return words_list

# function that remove the tokens whose indexes 
# are in the indexes list parameter
def del_list_indexes(l, id_to_del):
    somelist = [value for idx, value in enumerate(l) if idx not in id_to_del]
    return somelist

def count_tags_occurrences(filepath_jsonl, floats=False):
    with open(filepath_jsonl, "r", encoding="utf-8") as json_file:
        json_list = list(json_file)

    labels_occurences_dict = dict()
    ner_tags = []
    for json_idx, json_sequence in enumerate(json_list):
        data = json.loads(json_sequence)
        tags = data["ner_tags"]
        ner_tags.extend(tags)

    n_labels = len(ner_tags)
    ner_tags_set = set(ner_tags)
    ner_tags_unique = [label[2:] if label != "O" else label for label in ner_tags_set]

    ner = [label[2:] if label != "O" else label for label in ner_tags]
    labels_occurences_dict_str = {label:  str(round((ner.count(label) / n_labels) * 100, 2)) + " %"  for label in ner_tags_unique}
    labels_occurences_dict_floats = {label: round((ner.count(label) / n_labels) * 100, 2) for label in ner_tags_unique}

    return labels_occurences_dict_floats if floats else labels_occurences_dict_str

def save_np_array(filepath, np_array):
    with open(filepath, 'wb') as f:
        np.save(f, np_array)

def save_list(filepath, list):
    with open(filepath, 'wb') as f:
        pickle.dump(list, f)

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

# function to check the presence of common abbreviations used in medical reports
def contains_abbreviations(string):
  regex = re.compile('.*(sig|dott|prof|art|anest|tel|es|osp|val|coeff|dr|chir|paz|pag|sec|sigra|dottssa|dottri|sigre|pol|proc|am|thorac|wd)\s*$')
  return regex.search(string.lower()) is not None

# function to generate sentences starting from narrative text
def sentence_preprocessing(ehr_words, ner_tags, narrative_flag=False):

    # let found all dots that are sentence separators
    dots_indices = [idx for idx, dot in enumerate(ehr_words) if dot == "."  and ((idx-1)>=0 and contains_abbreviations(ehr_words[idx-1]))==False and ((idx+1)<len(ehr_words) and ehr_words[idx+1].isdigit() == False and "%" not in ehr_words[idx+1] and "ng/ml" not in ehr_words[idx+1] and "ng" not in ehr_words[idx+1] and "cm" not in ehr_words[idx+1] and not re.search(r"\d+x\d+", ehr_words[idx+1]) and not re.search(r"^it", ehr_words[idx+1]) and not re.search(r"www", ehr_words[idx-1])) and ((idx-1)>=0 and not re.search(r"@", ehr_words[idx-1]) and not re.search(r"^[a-zA-Z]$", ehr_words[idx-1]))]
    # adding the index of last word in the text
    dots_indices.append(len(ehr_words)-1)
    
    keywords = ["Raccordo", "EI", "Anamnesi", "ECOG"] #, "Notizie"]

    # let find occurrences of "\n\n" or greater
    # their indexes are added to separators
    backslash_indices = []
    for idx, token in enumerate(ehr_words):
        if idx+1 < len(ehr_words) and idx-1 >= 0 and token == "\n" and ehr_words[idx+1] == "\n" and ehr_words[idx-1] != "," and ehr_words[idx-1] not in keywords:
            num_newlines = 1
            while idx + num_newlines <len(ehr_words) and ehr_words[idx + num_newlines] == "\n":
                num_newlines += 1
            if (idx + num_newlines -1) not in backslash_indices:
                backslash_indices.append(idx+ num_newlines - 1)

    dots_indices = dots_indices + backslash_indices
    dots_indices.sort(reverse=False)

    # let find the narrative part in the reports
    # don't use it if you have text preprocessing (narrative_flag is False)
    if narrative_flag:
        relevant_words = []
        relevant_tags = []
        for i, token in enumerate(ehr_words):
            if (i+1)<len(ehr_words) and 'notizie' in token.lower() and 'cliniche' in ehr_words[i+1].lower():
                # se il token corrente è una parola chiave, aggiungi i token successivi a relevant_tokens
                relevant_words.extend(ehr_words[i:])
                relevant_tags.extend(ner_tags[i:])
                dots_indices = [(dot_idx-(i)) for dot_idx in dots_indices if dot_idx >= i+2]
                break
            elif (i+1)<len(ehr_words) and 'esami' in token.lower() and ':' in ehr_words[i+1].lower():
                # se il token corrente è una parola chiave, aggiungi i token successivi a relevant_tokens
                relevant_words.extend(ehr_words[i:])
                relevant_tags.extend(ner_tags[i:])
                dots_indices = [(dot_idx-(i)) for dot_idx in dots_indices if dot_idx >= i+2]
                break
            elif (i+2)<len(ehr_words) and 'referto' in token.lower() and 'di' in ehr_words[i+1].lower() and 'visita' in ehr_words[i+2].lower():
                # se il token corrente è una parola chiave, aggiungi i token successivi a relevant_tokens
                relevant_words.extend(ehr_words[i:])
                relevant_tags.extend(ner_tags[i:])
                dots_indices = [(dot_idx-(i)) for dot_idx in dots_indices if dot_idx >= i+3]
                break
            elif (i+3)<len(ehr_words) and 'referto' in token.lower() and 'di' in ehr_words[i+1].lower() and 'prima' in ehr_words[i+2].lower() and 'visita' in ehr_words[i+3].lower():
                # se il token corrente è una parola chiave, aggiungi i token successivi a relevant_tokens
                relevant_words.extend(ehr_words[i:])
                relevant_tags.extend(ner_tags[i:])
                dots_indices = [(dot_idx-(i)) for dot_idx in dots_indices if dot_idx >= i+3]
                break
            elif (i+2)<len(ehr_words) and 'storia' in token.lower() and 'clinica' in ehr_words[i+1].lower() and 'oncologica' in ehr_words[i+2].lower():
                # se il token corrente è una parola chiave, aggiungi i token successivi a relevant_tokens
                relevant_words.extend(ehr_words[i:])
                relevant_tags.extend(ner_tags[i:])
                dots_indices = [(dot_idx-(i)) for dot_idx in dots_indices if dot_idx >= i+3]
                break
            else:
                if (token.lower() == "paziente" and ehr_words[i+1].lower() == "di") | (token.lower() == "paziente" and ehr_words[i+1].lower() == "in"):
                    relevant_words.extend(ehr_words[i:])
                    relevant_tags.extend(ner_tags[i:])
                    dots_indices = [(dot_idx-(i)) for dot_idx in dots_indices if dot_idx >= i]
                    break

        
        # deleting last part of report
        for i, token in enumerate(relevant_words):

            if (i+2)<len(relevant_words) and (('il' in token.lower() and 'medico' in relevant_words[i+1].lower() and 'responsabile' in relevant_words[i+2].lower()) |('grading' in token.lower() and 'medico' in relevant_words[i+1].lower()) | ('il' in token.lower() and 'radioterapista' in relevant_words[i+1].lower() and 'oncologo' in relevant_words[i+2].lower()) | ('medico' in token.lower() and ':' in relevant_words[i+1].lower())) :
                dots_indices = [dot_idx for dot_idx in dots_indices if dot_idx <= (i-1)]
                dots_indices.append(i-1)
                break
            elif (i+1)<len(relevant_words) and ('radioterapia' in token.lower() and 'trigoria' in relevant_words[i+1].lower()):
                dots_indices.append(i-1)
                dots_indices.sort()
            elif (i+6)<len(relevant_words) and ('università' in token.lower() and 'campus' in relevant_words[i+1].lower() and 'roma' in relevant_words[i+6].lower()):
                dots_indices.append(i-1)
                dots_indices.sort()
            elif  (((i+3)<len(relevant_words) and 'via' in token.lower() and 'àlvaro' in relevant_words[i+1].lower() and 'del' in relevant_words[i+2].lower() and 'portillo' in relevant_words[i+3].lower())|((i+6)<len(relevant_words) and 'università' in token.lower() and 'Roma' in relevant_words[i+6])):
                for j in range(i, len(relevant_words)):
                    if (j+4)<len(relevant_words) and ('www'in relevant_words[j].lower() and 'policlinicocampusbiomedico' in relevant_words[j+2].lower()):
                        dots_indices_1 = [dot_idx for dot_idx in dots_indices if dot_idx < (i-1)]
                        dots_indices_2 = [dot_idx for dot_idx in dots_indices if dot_idx > (j+4)]
                        dots_indices = dots_indices_1 + dots_indices_2
                        dots_indices.append(i-1)
                        dots_indices.append(j+4)
                        dots_indices.sort()
                        break
    else:
        relevant_words = ehr_words
        relevant_tags = ner_tags 
    
    # sentences generation by considering collected separators 
    sentences = []
    ner_tags_sentences = []
    word_start = 0
    for dot_idx in dots_indices:
        if narrative_flag:
            sentence_len = 0
            if(len(relevant_words[word_start:dot_idx+1]) > 0):
                for idx in range(word_start,dot_idx+1):
                    if relevant_words[idx] != "\n":
                        sentence_len += 1
                if sentence_len > 1:
                    sentences.append(relevant_words[word_start:dot_idx+1])
                    ner_tags_sentences.append(relevant_tags[word_start:dot_idx+1])
                word_start = dot_idx+1
        else:
            if len(relevant_words[word_start:dot_idx+1]) != 0:
                sentences.append(relevant_words[word_start:dot_idx+1])
                ner_tags_sentences.append(relevant_tags[word_start:dot_idx+1])
                word_start = dot_idx+1 
    
    if narrative_flag:
        idx_to_del1 = [idx for idx, sentence in enumerate(sentences) if ("Radioterapia" in sentence and "Trigoria" in sentence)] 
        idx_to_del2 = [idx+1 for idx, sentence in enumerate(sentences) if ("Radioterapia" in sentence and "Trigoria" in sentence)]   
        idx_to_del = idx_to_del1 + idx_to_del2
        sentences = del_list_indexes(sentences, idx_to_del)
        ner_tags_sentences = del_list_indexes(ner_tags_sentences, idx_to_del)

        idx_to_del = [idx for idx, sentence in enumerate(sentences) if "policlinicocampusbiomedico" in sentence]    
        sentences = del_list_indexes(sentences, idx_to_del)
        ner_tags_sentences = del_list_indexes(ner_tags_sentences, idx_to_del)

        idx_to_del = [idx for idx, sentence in enumerate(sentences) if "Università" in sentence and "Campus" in sentence and "Roma" in sentence]    
        sentences = del_list_indexes(sentences, idx_to_del)
        ner_tags_sentences = del_list_indexes(ner_tags_sentences, idx_to_del)

        idx_to_del = [idx for idx, sentence in enumerate(sentences) if "it" in sentence]   
        sentences = del_list_indexes(sentences, idx_to_del)
        ner_tags_sentences = del_list_indexes(ner_tags_sentences, idx_to_del)
        
        idx_to_del = [idx for idx, sentence in enumerate(sentences) if "Equipe" in sentence and "medica" in sentence]   
        sentences = del_list_indexes(sentences, idx_to_del)
        ner_tags_sentences = del_list_indexes(ner_tags_sentences, idx_to_del)

    # elimina le frasi i cui tag sono solo label "O"
    # idx_to_del = [idx for idx, tags in enumerate(ner_tags_sentences) if len(set(tags)) == 1] # COMMENTATO PER TEST SET
    # debug: check per vedere quali frasi sto eliminando
    # for i in idx_to_del:
    #     # print(ner_tags_sentences[i])
    #     print(sentences[i])
    # print(1)
    # sentences = del_list_indexes(sentences, idx_to_del)
    # ner_tags_sentences = del_list_indexes(ner_tags_sentences, idx_to_del) # COMMENTATO PER TEST SET


    # Split frasi in base a date nella forma "dd/mm/yyyy"
    # datetime_indices = [[idx for idx, word in enumerate(sentence) if len(word) == 10 and is_date(word)] for sentence in sentences]

    # datetime_split_sentences = []
    # datetime_split_ner_tags = []
    # for sentence_datetimes, sentence, ner_tags in zip(datetime_indices, sentences, ner_tags_sentences):
    #     if len(sentence_datetimes) == 0:
    #         datetime_split_sentences.append(sentence)
    #         datetime_split_ner_tags.append(ner_tags)

    #         continue
    #     elif len(sentence_datetimes) > 1:
    #         for first_datetime_idx, second_datetime_idx in zip(sentence_datetimes, sentence_datetimes[1:]):
    #             datetime_split_sentences.append(sentence[:first_datetime_idx+1])
    #             datetime_split_sentences.append(sentence[first_datetime_idx+1:second_datetime_idx+1])
                
    #             datetime_split_ner_tags.append(ner_tags[:first_datetime_idx+1])
    #             datetime_split_ner_tags.append(ner_tags[first_datetime_idx+1:second_datetime_idx+1])
                
    #             datetime_split_sentences.append(sentence[second_datetime_idx+1:])
    #             datetime_split_ner_tags.append(ner_tags[second_datetime_idx+1:])
                
    #             # print(first_datetime_idx, "\t", second_datetime_idx)
    #     else:
    #         datetime_split_sentences.append(sentence[:sentence_datetimes[0]+1])
    #         datetime_split_ner_tags.append(ner_tags[:sentence_datetimes[0]+1])
        
    #         datetime_split_sentences.append(sentence[sentence_datetimes[0]+1:])
    #         datetime_split_ner_tags.append(ner_tags[sentence_datetimes[0]+1:])

    # idx_to_del = [idx for idx, tags in enumerate(datetime_split_ner_tags) if len(set(tags)) == 1] COMMENTATO FOR TEST
    # sentences = del_list_indexes(datetime_split_sentences, idx_to_del)
    # ner_tags_sentences = del_list_indexes(datetime_split_ner_tags, idx_to_del)
    # sentences = datetime_split_sentences
    # ner_tags_sentences = datetime_split_ner_tags

    # temp_sentences = sentences[:]
    # temp_ner_tags_sentences = ner_tags_sentences[:]
    # for key in keywords:
    #     temp_sentences = temp_sentences[:]
    #     temp_ner_tags_sentences = temp_ner_tags_sentences[:]
        # for idx, sentence_ner_tags in enumerate(zip(temp_sentences, temp_ner_tags_sentences)):
            # if key == "Notizie":
            #     if key in sentence_ner_tags[0] and sentence_ner_tags[0][0] != key and sentence_ner_tags[0][sentence_ner_tags[0].index(key)+1] == "cliniche":
            #         key_idx = sentence_ner_tags[0].index(key)
            #         first_split = sentence_ner_tags[0][:key_idx]
            #         second_split = sentence_ner_tags[0][key_idx:]
                    
            #         temp_sentences.pop(idx)
            #         temp_sentences.insert(idx, first_split)
            #         temp_sentences.insert(idx+1, second_split)

            #         first_split_ner_tags = sentence_ner_tags[1][:key_idx]
            #         second_split_ner_tags = sentence_ner_tags[1][key_idx:]

            #         temp_ner_tags_sentences.pop(idx)
            #         temp_ner_tags_sentences.insert(idx, first_split_ner_tags)
            #         temp_ner_tags_sentences.insert(idx+1, second_split_ner_tags)
            #         continue
            #     else:
            #         continue

            # if key in sentence_ner_tags[0] and sentence_ner_tags[0][0] != key:
            #     key_idx = sentence_ner_tags[0].index(key)
            #     first_split = sentence_ner_tags[0][:key_idx]
            #     second_split = sentence_ner_tags[0][key_idx:]
                
            #     temp_sentences.pop(idx)
            #     temp_sentences.insert(idx, first_split)
            #     temp_sentences.insert(idx+1, second_split)

            #     first_split_ner_tags = sentence_ner_tags[1][:key_idx]
            #     second_split_ner_tags = sentence_ner_tags[1][key_idx:]

            #     temp_ner_tags_sentences.pop(idx)
            #     temp_ner_tags_sentences.insert(idx, first_split_ner_tags)
            #     temp_ner_tags_sentences.insert(idx+1, second_split_ner_tags)

    # sentences = temp_sentences[:]
    # ner_tags_sentences = temp_ner_tags_sentences[:]


    temp_sentences = []
    temp_ner_tags_sentences = []
    # Deleting the first and last elements in a sentence that are "\n"
    for idx, sentence_ner_tags in enumerate(zip(sentences, ner_tags_sentences)):
        sentence = sentence_ner_tags[0]
        tags = sentence_ner_tags[1]
        sentences_temp = []
        ner_tags_sentences_temp = []

        if sentence_ner_tags[0][0] == "\n" and sentence_ner_tags[0][-1] == "\n" and len(set((sentence_ner_tags[0]))) != 1:
            # relevant_word = next(word for word in sentence if word != "\n") # trova la prima parola nellla lista diversa da \n
            # relevant_word_idx = sentence.index(relevant_word)
            relevant_word_indices = [idx for idx, word in enumerate(sentence) if word != "\n"]
            relevant_word_idx = relevant_word_indices[0]
            
            sentences_temp = sentence_ner_tags[0][relevant_word_idx:]
            ner_tags_sentences_temp = sentence_ner_tags[1][relevant_word_idx:]

            sentences_temp.reverse()
            ner_tags_sentences_temp.reverse()
            relevant_word_reversed = next(word for word in sentences_temp if word != "\n")
            relevant_word_idx_reversed = sentences_temp.index(relevant_word_reversed)

            sentences_temp = sentences_temp[relevant_word_idx_reversed:]
            ner_tags_sentences_temp = ner_tags_sentences_temp[relevant_word_idx_reversed:]

            sentences_temp.reverse()
            ner_tags_sentences_temp.reverse()

            temp_sentences.append(sentences_temp)
            temp_ner_tags_sentences.append(ner_tags_sentences_temp)

        elif sentence_ner_tags[0][0] == "\n" and len(set((sentence_ner_tags[0]))) != 1:
            # relevant_word = next(word for word in sentence if word != "\n")
            # relevant_word_idx = sentence.index(relevant_word)
            relevant_word_indices = [idx for idx, word in enumerate(sentence) if word != "\n"]
            relevant_word_idx = relevant_word_indices[0]

            sentences_temp = sentence_ner_tags[0][relevant_word_idx:]
            ner_tags_sentences_temp = sentence_ner_tags[1][relevant_word_idx:]
            
            temp_sentences.append(sentence_ner_tags[0][relevant_word_idx:])
            temp_ner_tags_sentences.append(sentence_ner_tags[1][relevant_word_idx:])
        
        else:
            if len(set((sentence_ner_tags[0]))) != 1:
                temp_sentences.append(sentence_ner_tags[0])
                temp_ner_tags_sentences.append(sentence_ner_tags[1])

    # sentences = temp_sentences[:]
    # ner_tags_sentences = temp_ner_tags_sentences[:]
    sentences = []
    ner_tags_sentences = []
    # deleting \n
    for sent, tags in zip(temp_sentences, temp_ner_tags_sentences):
        undesired_chars_idx = [index for index, word in enumerate(sent) if word == "\n"]   
        sent = del_list_indexes(sent, undesired_chars_idx)
        tags = del_list_indexes(tags, undesired_chars_idx)
        sentences.append(sent)
        ner_tags_sentences.append(tags)
    return sentences, ner_tags_sentences

if __name__ == "__main__":
    
    name = "doccano"
    # name = "doccano_test"   
    filename = f"./doccano/jsonl/{name}.jsonl"
    txt = 'PolmoneCarcinoma squamoso'
    # txt = "NostalgiaCanagliaDi "
    # txt = "logicaTa)"
    # txt = "ECOG: 0: paz. attivo, "
    # txt = '78 anniID Paziente'
    s = get_words(txt)
    print(txt)
    print(s)
