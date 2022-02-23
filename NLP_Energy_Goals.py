from PyPDF2 import PdfFileWriter, PdfFileReader
from urllib.request import urlopen, Request
import pandas as pd
from pandas import DataFrame
import requests
import spacy
import os
from collections import Counter
from io import StringIO, BytesIO
import re 
import matplotlib.pyplot as plt
import wordcloud 
import bokeh
from bokeh.io import output_file, show
from bokeh.layouts import gridplot
from bokeh.models.widgets import Tabs, Panel, TableColumn, DataTable
from bokeh.models import ColumnDataSource, HoverTool
import bokeh.palettes
import wordtodigits
from bokeh.plotting import figure


##Sources: 
    #Word to number: https://pypi.org/project/word2number/
    #NLP Counting frequencies: https://github.com/kamal2230/text-summarization/blob/master/Summarisation_using_spaCy.ipynb
    #NLP find dependencies: Data & Programming Lecture 9
    #NLP identify dependencies: https://spacy.io/usage/linguistic-features
    #NLP Looping: https://github.com/ines/spacy-course/blob/master/exercises/en/solution_01_04.py
    #Final Goal plots: Data & Programming Interactive Plotting Lecture
    
nlp = spacy.load('en_core_web_sm')

url = "https://www.un.org/millenniumgoals/pdf/SEFA.pdf"

def extract_pdf(url):
    '''find pdf and extract the text'''
    url = url
    html = urlopen(url).read()
    memoryFile = BytesIO(html)
    pdfReader = PdfFileReader(memoryFile)
    number_of_pages = pdfReader.getNumPages()

    for page in range(number_of_pages):
        pageObj = pdfReader.getPage(page)
        pdftext = pageObj.extractText().replace('\n','').encode('ascii', 'ignore')
        return str(pdftext)
    
text = extract_pdf(url)
doc = nlp(text)

def summarize_frequency(doc):
    '''Creates a frequency table, word cloud, Bokeh output'''
    tokens = [token.lemma_ for token in doc if token.is_stop != True and token.is_punct != True] 
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
    clean = [s.strip("''") for s in tokens]
    frequency = Counter(clean)
    topwords = frequency.most_common(10)
    topwords = [i for i in topwords if i[0] != ' ']
    topwords = [(keyword.capitalize(), entries) for keyword, entries in topwords]
    
    topwords.sort(key=lambda x: x[1], reverse=True) 
    word = list(zip(*topwords))[0]
    count = list(zip(*topwords))[1]
    
    for ent in doc.ents:
        if ent.label_ in ["PERSON","ORG"]:
            ents = [e.text for e in doc.ents]
    for i in range(len(ents)):
        ents[i] = ents[i].lower()
    clean_ents = [s.strip("''") for s in ents]
    frequency_ents = Counter(clean_ents)
    topwords_ents = frequency_ents.most_common(20)
    topwords_ents = [i for i in topwords_ents if i[0] != ' ']
    topwords_ents = [(keyword.capitalize(), entries) for keyword, entries in topwords_ents]
    
    topwords_ents.sort(key=lambda x: x[1], reverse=True) 
    word_ent = list(zip(*topwords_ents))[0]
    pattern = re.compile(r"[^a-zA-Z ]")
    word_ent = [pattern.sub("", item) for item in word_ent]
    word_ent = list(filter(None, word_ent))

    ent_df = DataFrame(word_ent,columns=['Actors'])
    ent_src = ColumnDataSource(ent_df)
      
    p1 = figure(x_range=word, plot_height=250, title="Most Frequent Words")
    p1.vbar(x=word, top=count, width=0.8, color=bokeh.palettes.viridis(9))

    tab1 = Panel(child = p1, title = 'Key Words')
    
    
    table_columns = [TableColumn(field='Actors', title='Key Actors mentioned')]
    p2 = DataTable(source=ent_src, 
                              columns=table_columns, width=1000)
    tab2 = Panel(child = p2, title = 'Key Actors Table')
    tabs_object = Tabs(tabs = [tab1, tab2])

    show(tabs_object)
    
    for_wc = str(tokens)
    wc = wordcloud.WordCloud(random_state =1, background_color='salmon', colormap='Pastel1').generate(for_wc)
    wc.to_file('freq_cloud.png')
    plt.figure(figsize=(40,30))
    plt.imshow(wc)
    
    return tabs_object, wc 

def define_timeline(doc):
    '''defines the timeline and objective of UN energy goals'''
    year = [x + 2000 for x in range(40)]
    year = [str(y) for y in year]
    goal_frame= ["Launched", "achieved", "support", "created", "goal", "set"]
    
    for sent in doc.sents:
        goal = [e for e in sent if e.text in goal_frame]
        selected_years = [y for y in sent if y.text in year]
        timeline = [(g, y) for g, y in zip(goal, selected_years)]
        for l in timeline:
            if (len(l)>0):
                print(f'UN Energy Timeline: {l}')
                   
    word = ['Double', 'Triple', 'Maintain', 'Sustain', 'Create', 'Protect', 'Safeguard', 'Ensure'] 
    sentences = list(doc.sents)
    length = len(sentences)
    
    for i in range(length):
        sent = list(doc.sents)[i]
        for token in sent:
            if(token.text in word):
                measure = token.text
                children = [children for children in token.children if children.pos_ == "NOUN"] 
                ancestors = [cp for cp in token.ancestors if cp.pos_ == 'NOUN']
                relatives = children + ancestors
                print(f'Action: {measure}, Type: {relatives}')

summarize_frequency(doc)
define_timeline(doc)

