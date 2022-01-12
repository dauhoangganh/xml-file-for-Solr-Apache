#!/usr/bin/env python
# coding: utf-8

# In[6]:


import argparse
import os
#import regex as re
import re
import csv
#schema.xml のdefault Field type
FIELD_TYPE='''<schema name="field definition" version="1.1">
    <types>
        <fieldType name="string" class="solr.StrField" sortMissingLast="true"></fieldType>
        <fieldType name="boolean" class="solr.BoolField" sortMissingLast="true"></fieldType>

        <fieldType name="int" class="solr.TrieIntField" precisionStep="0" positionIncrementGap="0"></fieldType>
        <fieldType name="float" class="solr.TrieFloatField" precisionStep="0" positionIncrementGap="0"></fieldType>
        <fieldType name="long" class="solr.TrieLongField" precisionStep="0" positionIncrementGap="0"></fieldType>
        <fieldType name="double" class="solr.TrieDoubleField" precisionStep="0" positionIncrementGap="0"></fieldType>

        <fieldType name="tint" class="solr.TrieIntField" precisionStep="8" positionIncrementGap="0"></fieldType>
        <fieldType name="tfloat" class="solr.TrieFloatField" precisionStep="8" positionIncrementGap="0"></fieldType>
        <fieldType name="tlong" class="solr.TrieLongField" precisionStep="8" positionIncrementGap="0"></fieldType>
        <fieldType name="tdouble" class="solr.TrieDoubleField" precisionStep="8" positionIncrementGap="0"></fieldType>

        <fieldtype name="binary" class="solr.BinaryField"></fieldtype>

        <fieldType name="pint" class="solr.IntField"></fieldType>
        <fieldType name="plong" class="solr.LongField"></fieldType>
        <fieldType name="pfloat" class="solr.FloatField"></fieldType>
        <fieldType name="pdouble" class="solr.DoubleField"></fieldType>
        <fieldType name="pdate" class="solr.DateField" sortMissingLast="true"></fieldType>
        <fieldType name="text_cjk" class="solr.TextField">
            <analyzer class="org.apache.lucene.analysis.cjk.CJKAnalyzer" />
        </fieldType>
        <fieldType name="text_ja" class="solr.TextField" positionIncrementGap="100" autoGeneratePhraseQueries="true">
            <analyzer class="org.apache.lucene.analysis.ja.JapaneseAnalyzer"/>
            <analyzer type="index">
            <tokenizer class="solr.KuromojiTokenizerFactory" mode="extended"
            user-dictionary="userdict.txt" user-dictionary-encoding="UTF-8"/>
            <tokenizer class="solr.KuromojiTokenizerFactory" mode="search"/>
            <filter class="solr.KuromojiBaseFormFilterFactory"/>
            <filter class="solr.KuromojiPartOfSpeechStopFilterFactory"
                tags="lang/stoptags_ja.txt" enablePositionIncrements="true"/>
            <filter class="solr.CJKWidthFilterFactory"/>
            <tokenizer class="solr.ClassicTokenizerFactory"/>
            <tokenizer class="solr.WhitespaceTokenizerFactory"/>
            <filter class="solr.LowerCaseFilterFactory"/>
            <filter class="solr.StopFilterFactory" ignoreCase="true" words="stopwords_ja.txt" enablePositionIncrements="true" />
            <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1" 
                    catenateWords="1" catenateNumbers="1" catenateAll="0" splitOnCaseChange="0" preserveOriginal="1"/>
            </analyzer>
        </fieldType>
        <fieldType name="float" class="solr.FloatField" omitNorms="true"/>
        <fieldType name="double" class="solr.DoubleField" omitNorms="true"/>
    </types>
    '''
#convert CSV to data.xml and schema.xml
def convertCSV2XML(args):
    with open(os.path.join(args.InputDir, args.InputCSV), 'r', encoding='utf8') as file:
        lines1=file.read()
    lines1=re.sub('&', '&amp;', lines1) #replace & by &amp;
    lines1=re.sub('<', '&lt;', lines1)  #replace < by &lt;
    lines1=re.sub('>', '&gt;', lines1)  #replace > by &gt;
    lines1=re.sub('\ufeff', '', lines1)
    
    infiles=sorted(os.listdir(args.InputDir))   #arrange CSV files in order

    with open (os.path.join(args.InputDir, args.InputCSV), 'w', encoding='utf8') as f:
        f.write(lines1)

    with open(os.path.join(args.InputDir, args.InputCSV), 'r', encoding='utf8') as csvfile:
        file=csv.reader(csvfile, skipinitialspace=True, escapechar='\\', quotechar='"', doublequote=True)
        field_names=next(file) #get the field names list (first row of CSV)
        
        lines=[]
        for i, line in enumerate(file):
            if i==0:
                field_types=line #get field types list (second row of CSV)
            elif i==1:
                field_flags=line #get field tags list (third row of CSV)
            elif i>1:
                lines.append(line) #list of data rows
    with open('stop.txt', 'r', encoding='utf8', ) as stopfile:
        stopwords=stopfile.readlines()
    stopwords=[i.strip() for i in stopwords]
    with open(os.path.join(args.OutputDir,"data.xml"), 'w', encoding='utf8') as file2: #write to data.xml file
    # Write contents to the data.xml file here
        file2.write('<?xml version="1.0" ?>\n')
        file2.write('<add>\n')
        for u in range(0, len(lines)):
            file2.write('\t<doc>\n')
            for i, j in zip(field_names, lines[u]):
                if i==args.targetFieldname:
                    j=j.split('|') 
                    kw=[] #list of keywords
                    kw2=[] #list of (keyword+tfidf+frequency)
                    for v in j:
                        m=[i for i in v.split('/')]
                        kw.append(m[0]) 
                        kw2.append(v)
                    for n in range(0, len(kw)):
                        if not re.match(r'^[_\W]+$', kw[n]): #ignore keywords with only special characters
                            kw[n]=re.sub(r'[^A-Za-z0-9\u4E00-\u9FD0あ-ん\u30A1-\u30F4ー　Ａ-Ｚａ-ｚ０-９ ]+','', kw[n]) #subtitute all special character except Hiragana, kanji, katakana, space, romaji with ''
                            kw[n]=re.sub(r'(?<=[^A-Za-z0-9０-９Ａ-Ｚａ-ｚ])\s(?=[^A-Za-z0-9０-９Ａ-Ｚａ-ｚ])', '', kw[n]) #remove space between Jpese words
                            kw[n]=kw[n].strip()
                            if kw[n] not in stopwords:
                                file2.write(f"\t\t<field name='keywordFacet'>{kw[n]}</field>\n") #remove space at the beginning and the end of keywords
                    for n in range(0, len(kw2)): 
                        if not re.match(r'^[_\W]+$', kw[n]) and (kw[n] not in stopwords):
                            file2.write(f"\t\t<field name='keyword'>{kw2[n]}</field>\n")
                
            for i, j in zip(field_names, lines[u]):
                if i != args.targetFieldname and i!='keyword':
                    file2.write(f"\t\t<field name=\'{i}\'>{j}</field>\n")
            db_name=re.sub(r'^(\w+)_(\d+)\.txt$', '\\1\\2', args.InputCSV)
            db_id=infiles.index(args.InputCSV)
            file2.write(f'\t\t<field name="doc_id">{db_id}_{u+1}</field>\n')
            file2.write(f'\t\t<field name="db_id">{db_id}</field>\n')
            file2.write(f'\t\t<field name="db_name">{db_name}</field>\n')
            file2.write('\t</doc>\n')
        file2.write('</add>')
    
    with open(os.path.join(args.OutputDir,"schema.xml"), 'w', encoding='utf8') as file1:
        # Write contents to the schema file here
        file1.write(FIELD_TYPE)
        file1.write('<fields>\n')
        for n, t, f in zip(field_names, field_types, field_flags):
            if f=='0':
                if n==args.targetFieldname:
                    file1.write(f'<field name=\'{n}\' type="string" indexed="true" termOffsets="true" stored="true" termVectors="true" termPositions="true" multiValued="true"><MimaSearch hidden="true" keyword="false" facet="true"></MimaSearch>\n')
                    file1.write('</field>\n')
                elif n== 'keyword':
                    file1.write(f'<field name=\'{n}\' type="string" indexed="true" termOffsets="true" stored="true" termVectors="true" termPositions="true"><MimaSearch hidden="true" keyword="false" facet="true"></MimaSearch>\n')
                    file1.write('</field>\n')
                elif n in {'doc_id', 'db_id', 'db_name'}:
                    file1.write(f'<field name=\'{n}\' type="string" indexed="true" termOffsets="true" stored="true" termVectors="true" termPositions="true"><MimaSearch hidden="true"></MimaSearch>\n')
                    file1.write('</field>\n')
                else:
                    file1.write(f'<field name=\'{n}\' type="string" indexed="true" termOffsets="true" stored="true" termVectors="true" termPositions="true">\n')
                    file1.write('</field>\n')
            elif f=='1':
                file1.write(f'<field name=\'{n}\' type="text_ja" indexed="true" stored="true" termVectors="true" termPositions="true"><MimaSearch></MimaSearch>\n')
                file1.write('</field>\n')
            else:
                file1.write(f'<field name=\'{n}\' type="int" indexed="true" stored="true" termVectors="true" termPositions="true"><MimaSearch></MimaSearch>\n')
                file1.write('</field>\n')
        file1.write('</fields>\n')
        for n in list(field_names):
            file1.write(f'<copyField source=\'{n}\' dest="text"></copyField>\n')
        for i in {'doc_id', 'db_id'}:
            file1.write(f'<uniqueKey>{i}</uniqueKey>\n')
        file1.write('</schema>')

 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--InputCSV', required=True,help="name of input csv file")
    parser.add_argument('--DBName',required=False, help='Name of database')
    parser.add_argument('--DBID',required=False, help='database ID')
    parser.add_argument('--InputDir', required=True, help='path of input directory')
    parser.add_argument('--OutputDir',required=True, help='Path of output directory')
    parser.add_argument('--targetFieldname',required=True, help='name of the keyword field')
    args = parser.parse_args()
    convertCSV2XML(args)
   
 

