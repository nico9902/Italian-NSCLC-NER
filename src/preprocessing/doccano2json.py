"""
Script generating a json file of the dataset labeled on doccano (jsonl format).
In the json file each report is splitted in sentences and then each sentence is tokenized.
"""

# import libraries
import json
import argparse
from operator import itemgetter
from src.preprocessing.doccano_utils import get_words, del_list_indexes, sentence_preprocessing 

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert Doccano JSONL to tokenized JSON")
    parser.add_argument("--input_file", "-i", required=True, help="Path to input Doccano JSONL file")
    args = parser.parse_args()

    filename = args.input_file

    # read doccano file
    with open(filename, 'r', encoding="utf-8") as json_file:
        json_list = list(json_file)

    count = 0  # for debug
    # report processing
    for json_idx, json_str in enumerate(json_list):
        ehr = json.loads(json_str)
        ehr_id = ehr['id']
        ehr_text = ehr["text"]

        start_pos = 0
        if start_pos is not None:
            ehr_words = get_words(ehr_text)
            ehr_labels = sorted(ehr["label"], key=itemgetter(0)) # sorting labels by order of occurence

            # Get ordered list of labels
            labels = [label_list[2] for label_list in ehr_labels]

            # Get list of position-characters of labels
            labels_chars_intervals_nested = [[label_list[0]-start_pos, label_list[1]-start_pos] for label_list in ehr_labels]
            labels_chars_intervals = [item for sublist in labels_chars_intervals_nested for item in sublist]
            labels_chars_starts = labels_chars_intervals[0::2]

            ner_tags = []
            chars_length_count = 0
            label_start = -5
            label_end = -10

            for idx, word in enumerate(ehr_words):
    
                if chars_length_count in range(label_start, label_end): # skip characters that are labeled
                    #print(word, idx, chars_length_count, len(ner_tags), ner_tags[-1])
                    chars_length_count += len(word)
                    continue
            
                if chars_length_count in labels_chars_starts: # check if the char number is the start of a label
                    # Get corresponding label by index
                    ner_tag_idx = [(i, el.index(chars_length_count)) for i, el in enumerate(labels_chars_intervals_nested) if chars_length_count in el][0]
                    ner_tag_idx = ner_tag_idx[0]
                    ner_tag = labels[ner_tag_idx]

                    # Get starting and ending char for the label
                    label_start = chars_length_count
                    if (labels_chars_intervals.index(label_start)+1)<len(labels_chars_intervals) and labels_chars_intervals[labels_chars_intervals.index(label_start)] == labels_chars_intervals[labels_chars_intervals.index(label_start)+1]:
                        label_end_idx = labels_chars_intervals.index(label_start) + 2
                    else:
                        label_end_idx = labels_chars_intervals.index(label_start) + 1
                    label_end = labels_chars_intervals[label_end_idx]

                    labeled_text = ehr_text[label_start:label_end]
                    labeled_words = get_words(labeled_text)

                    if len(labeled_words) == 1:     # check if it is a one-word-label
                        ner_tags.append("B-" + ner_tag)
                    else:
                        ner_tags_temp = ["B-" + ner_tag if idx == 0 else "I-" + ner_tag for idx, word in enumerate(labeled_words)]
                        ner_tags.extend(ner_tags_temp)
                else:
                    ner_tags.append("O")

                chars_length_count += len(word)

            print(json_idx)
            print("ner_tags:", len(ner_tags))
            print("ehr_words:", len(ehr_words))

            # Clear list of words from undesired characters
            undesired_chars = ["", " ", "\x0c"] #aggiunto \x0c, \f ed eliminato \n
            undesired_chars_idx = [index for index, char in enumerate(ehr_words) if char in undesired_chars]
            
            ehr_words = del_list_indexes(ehr_words, undesired_chars_idx)
            ner_tags = del_list_indexes(ner_tags, undesired_chars_idx)

            # Sentences generation
            sentences, tags = sentence_preprocessing(ehr_words, ner_tags, False)
         
            # Write JSON file
            if json_idx == 0:
                with open("./doccano/json/doccano_processed_329_instances.json", 'w', encoding="utf-8") as f:
                    for idx, sentence_ner_tags in enumerate(zip(sentences, tags)):
                        # data = {"id": str(ehr_id), "report_id": str(json_idx), "tokens": sentence_ner_tags[0], "ner_tags": sentence_ner_tags[1]}
                        data = {"id": str(ehr_id), "tokens": sentence_ner_tags[0], "ner_tags": sentence_ner_tags[1]}
                        f.write(json.dumps(data, ensure_ascii=False))
                        f.write('\n')
            else:
                with open("./doccano/json/doccano_processed_329_instances.json", 'a', encoding="utf-8") as f:
                    for idx, sentence_ner_tags in enumerate(zip(sentences, tags)):
                        # data = {"id": str(ehr_id), "report_id": str(json_idx), "tokens": sentence_ner_tags[0], "ner_tags": sentence_ner_tags[1]}
                        data = {"id": str(ehr_id), "tokens": sentence_ner_tags[0], "ner_tags": sentence_ner_tags[1]}
                        f.write(json.dumps(data, ensure_ascii=False))
                        f.write('\n')
        
        
            # Debug
            # if len(ner_tags) == len(ehr_words):
            #     # print(list(zip(ehr_words, ner_tags)))
            #     print(json_idx)
