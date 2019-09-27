import pandas as pd
import re
import sys
import requests
from lxml import etree


class RegExp():
    '''这里规定了所有提取条件的正则表达式，每一个self属性都必须是一个列表
    里面包含不定数目的正则，匹配时，程序会依次调用该字段下的正则，采取并集策略，返回结果
    '''
    def __init__(self):
        # toefl 正则表达式
        self.toefl_total = [
            r'(?:iBT|TOEFL|internet(?:-|\s)based).*?\D(1[0-1]\d|[7-9]\d|6[1-9])\D.*?(?:\s|minimum|at least|overall|total)',
            r'(?:iBT|TOEFL|internet(?:-|\s)based).*?(?:\s|minimum|at least|overall|total).*?\D(1[0-1]\d|[7-9]\d|6[1-9])(?:\D|$)',
            r'(?:^|\D)(1[0-1]\d|[7-9]\d|6[1-9])\D.*?(?:iBT|TOEFL|internet(?:-|\s)based).*?(?:\s|minimum|at least|overall|total)',
            r'(?:^|\D)(1[0-1]\d|[7-9]\d|6[1-9])\D.*?(?:\s|minimum|at least|overall|total).*?(?:iBT|TOEFL|internet(?:-|\s)based)',
            r'(?:minimum|at least|overall|total).*?(?:iBT|TOEFL|internet(?:-|\s)based).*?\D(1[0-1]\d|[7-9]\d|6[1-9])(?:\D|$)',
            r'(?:minimum|at least|overall|total).*?\D(1[0-1]\d|[7-9]\d|6[1-9])\D.*?(?:iBT|TOEFL|internet(?:-|\s)based)',
            r'(?:iBT|TOEFL|internet(?:-|\s)based).*?\D(1[0-1]\d|[7-9]\d|6[1-9])(?:\D|$)',
            r'(?:^|\D)(1[0-1]\d|[7-9]\d|6[1-9])\D.*?(?:iBT|TOEFL|internet(?:-|\s)based)'
        ]
        self.toefl_read = [
            r'reading[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:^|\D)(1[4-9]|2\d)[^\d,;.][^,;.]*?reading',
            r'reading,[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'no[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module).*?(?:below|lower|less)[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'reading, (?:listening|writing|(?:speaking|oral)),.*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:listening|writing|(?:speaking|oral)), reading,.*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:^|\D)(1[4-9]|2\d)\D.*?reading, (?:listening|writing|(?:speaking|oral))',
            r'(?:^|\D)(1[4-9]|2\d)[^\d,;.][^,;.]*?\b(?:(?:each|every|per|all|any|individual).*?(?:section|sub|area|component|band|categor|part|field|module))',
            r'\b(?:(?:each|every|per|all|any|individual)[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module))[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)'
        ]
        self.toefl_listen = [
            r'listening[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:^|\D)(1[4-9]|2\d)[^\d,;.][^,;.]*?listening',
            r'listening,[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'no[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module).*?(?:below|lower|less)[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'listening, (?:reading|writing|(?:speaking|oral)),.*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:reading|writing|(?:speaking|oral)), listening,.*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:^|\D)(1[4-9]|2\d)\D.*?listening, (?:reading|writing|(?:speaking|oral))',
            r'(?:^|\D)(1[4-9]|2\d)[^\d,;.][^,;.]*?\b(?:(?:each|every|per|all|any|individual).*?(?:section|sub|area|component|band|categor|part|field|module))',
            r'\b(?:(?:each|every|per|all|any|individual)[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module))[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)'
        ]
        self.toefl_speak = [
            r'(?:speaking|oral)[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:^|\D)(1[4-9]|2\d)[^\d,;.][^,;.]*?(?:speaking|oral)',
            r'(?:speaking|oral),[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'no[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module).*?(?:below|lower|less)[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:speaking|oral), (?:listening|writing|reading),.*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:listening|writing|reading), (?:speaking|oral),.*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:^|\D)(1[4-9]|2\d)\D.*?(?:speaking|oral), (?:listening|writing|reading)',
            r'(?:^|\D)(1[4-9]|2\d)[^\d,;.][^,;.]*?\b(?:(?:each|every|per|all|any|individual).*?(?:section|sub|area|component|band|categor|part|field|module))',
            r'\b(?:(?:each|every|per|all|any|individual)[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module))[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)'
        ]
        self.toefl_write = [
            r'writing[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:^|\D)(1[4-9]|2\d)[^\d,;.][^,;.]*?writing',
            r'writing,[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'no[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module).*?(?:below|lower|less)[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)',
            r'writing, (?:listening|reading|(?:speaking|oral)),.*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:listening|reading|(?:speaking|oral)), writing,.*?\D(1[4-9]|2\d)(?:\D|$)',
            r'(?:^|\D)(1[4-9]|2\d)\D.*?writing, (?:listening|reading|(?:speaking|oral))',
            r'(?:^|\D)(1[4-9]|2\d)[^\d,;.][^,;.]*?\b(?:(?:each|every|per|all|any|individual).*?(?:section|sub|area|component|band|categor|part|field|module))',
            r'\b(?:(?:each|every|per|all|any|individual)[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module))[^,;.]*?\D(1[4-9]|2\d)(?:\D|$)'
        ]
        self.toefl_code = [
            r'((?:\(|\b)(?:university|institution|college|school|SOPHAS|TOEFL|ETS)[^.,]*?code.*?\d{4}.*?(?:\)|\.))',
            r'((?:\(|\b)code[^.,]*?(?:university|institution|college|school|SOPHAS|TOEFL|ETS).*?\d{4}.*?(?:\)|\.))',
            r'((?:\(|\b)code[^.,]*?\d{4}[^.,]*?(?:university|institution|college|school|SOPHAS|TOEFL|ETS).*?(?:\)|\.))',
            r'((?:\(|\b)\d{4}[^.,]*?code[^.,]*?(?:university|institution|college|school|SOPHAS|TOEFL|ETS).*?(?:\)|\.))',
            r'((?:\(|\b)\d{4}[^.,]*?(?:university|institution|college|school|SOPHAS|TOEFL|ETS)[^.,]*?code.*?(?:\)|\.))'
        ]
        self.bool_toeflielts = [
            r'((?:iBT|TOEFL|internet(?:-|\s)based).*?or.*?ielts)',
            r'(ielts.*?or.*?(?:iBT|TOEFL|internet(?:-|\s)based))',
            r'(IELTS/TOEFL)',        
            r'(TOEFL/IELTS)'        
        ]
        # ielts 正则表达式   
        self.ielts_total = [
            r'IELTS.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])\D.*?(?:\s|minimum|overall|total)',
            r'IELTS.*?(?:\s|minimum|overall|total).*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])\D.*?IELTS.*?(?:\s|minimum|overall|total)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])\D.*?(?:\s|minimum|overall|total).*?IELTS',
            r'(?:minimum|overall|total).*?IELTS.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:minimum|overall|total).*?\D((?:[5-9](?:\)|\.)[05])|[5-9])\D.*?IELTS',
            r'(?:\s|minimum|overall|total).*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])\D.*?(?:\s|minimum|overall|total)'

        ]
        self.ielts_read = [
            r'reading[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])[^\d,;.][^,;.]*?reading',
            r'reading,[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'no[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module|score).*?(?:below|lower|less)[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'reading, (?:listening|writing|(?:speaking|oral)),.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:listening|writing|(?:speaking|oral)), reading,.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])\D.*?reading, (?:listening|writing|(?:speaking|oral))',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])[^\d,;.][^,;.(]*?\b(?:(?:each|every|per|all|any|individual).*?(?:section|sub|area|component|band|categor|part|field|module))',
            r'\b(?:(?:each|every|per|all|any|individual)[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module))[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)'
        ]
        self.ielts_listen = [
            r'listening[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])[^\d,;.][^,;.]*?listening',
            r'listening,[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'no[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module|score).*?(?:below|lower|less)[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'listening, (?:reading|writing|(?:speaking|oral)),.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:reading|writing|(?:speaking|oral)), listening,.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])\D.*?listening, (?:reading|writing|(?:speaking|oral))',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])[^\d,;.][^,;.(]*?\b(?:(?:each|every|per|all|any|individual).*?(?:section|sub|area|component|band|categor|part|field|module))',
            r'\b(?:(?:each|every|per|all|any|individual)[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module))[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)'
        ]
        self.ielts_speak = [
            r'(?:speaking|oral)[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])[^\d,;.][^,;.](?:speaking|oral)',
            r'(?:speaking|oral),[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'no[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module|score).*?(?:below|lower|less)[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:speaking|oral), (?:listening|writing|reading),.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:listening|writing|reading), (?:speaking|oral),.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])\D.*?(?:speaking|oral), (?:listening|writing|reading)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])[^\d,;.][^,;.(]*?\b(?:(?:each|every|per|all|any|individual).*?(?:section|sub|area|component|band|categor|part|field|module))',
            r'\b(?:(?:each|every|per|all|any|individual)[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module))[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)'
        ]
        self.ielts_write = [
            r'writing[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])[^\d,;.][^,;.]*?writing',
            r'writing,[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'no[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module|score).*?(?:below|lower|less)[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'writing, (?:listening|reading|(?:speaking|oral)),.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:listening|reading|(?:speaking|oral)), writing,.*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])\D.*?writing, (?:listening|reading|(?:speaking|oral))',
            r'(?:^|\D)((?:[5-9](?:\)|\.)[05])|[5-9])[^\d,;.][^,;.(]*?\b(?:(?:each|every|per|all|any|individual).*?(?:section|sub|area|component|band|categor|part|field|module))',
            r'\b(?:(?:each|every|per|all|any|individual)[^,;.]*?(?:section|sub|area|component|band|categor|part|field|module))[^,;.]*?\D((?:[5-9](?:\)|\.)[05])|[5-9])(?:\D|$)'
        ]

        # gmat 正则表达式
        self.gmat_total = [
            r'(?:gmat|(?:graduate management admission test)).*?\D([5-8]\d0)(?:\D|$)*?(?:\s|minimum|overall|total)',
            r'(?:gmat|(?:graduate management admission test)).*?(?:\s|minimum|overall|total).*?\D([5-8]\d0)(?:\D|$)',
            r'(?:^|\D)([5-8]\d0)\D.*?(?:gmat|(?:graduate management admission test)).*?(?:\s|minimum|overall|total)',
            r'(?:^|\D)([5-8]\d0)\D.*?(?:\s|minimum|overall|total).*?(?:gmat|(?:graduate management admission test))',
            r'(?:minimum|overall|total).*?(?:gmat|(?:graduate management admission test)).*?\D([5-8]\d0)(?:\D|$)',
            r'(?:minimum|overall|total).*?\D([5-8]\d0)\D.*?(?:gmat|(?:graduate management admission test))'
        ]
        self.gmat_verbal = [
            r'verbal[^.,;]*?minimum[^.,;]*?\D([3-4]\d|50|51)\b|[^(?:\d|th|%)]',
            r'verbal[^.,;]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?\D([3-4]\d|50|51)\b|[^(?:\d|th|%)]',
            r'verbal[^.,;]*?\D([3-4]\d|50|51)\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'(?:^|\D)([3-4]\d|50|51)\D[^(?:th|%)]*?verbal[^.,;]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'minimum.*?verbal[^.,;]*?\D([3-4]\d|50|51)\b|[^(?:\d|th|%)]',
            r'(?:above|below|no.*?(?:less|lower) than|higher|at least).*?verbal[^.,;]*?\D([3-4]\d|50|51)\b|[^(?:\d|th|%)]',            
            r'minimum[^.,;]*?\D([3-4]\d|50|51)\D[^(?:th|%|.,;)]*?verbal',
            r'(?:^|\D)([3-4]\d|50|51)\D[^(?:th|%)]*?minimum[^.,;]*?verbal',
            r'(?:^|\D)([3-4]\d|50|51)\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?verbal',
            r'(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?\D([3-4]\d|50|51)\D[^(?:th|%|.,;)]*?verbal'
        ]
        self.gmat_quantitative = [
            r'quantitative[^.,;]*?minimum[^.,;]*?\D([3-4]\d|50|51)\b|[^(?:\d|th|%)]',
            r'quantitative[^.,;]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?\D([3-4]\d|50|51)\b|[^(?:\d|th|%)]',
            r'quantitative[^.,;]*?\D([3-4]\d|50|51)\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'(?:^|\D)([3-4]\d|50|51)\D[^(?:th|%)]*?quantitative[^.,;]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'minimum.*?quantitative[^.,;]*?\D([3-4]\d|50|51)\b|[^(?:\d|th|%)]',
            r'(?:above|below|no.*?(?:less|lower) than|higher|at least).*?quantitative[^.,;]*?\D([3-4]\d|50|51)\b|[^(?:\d|th|%)]',            
            r'minimum[^.,;]*?\D([3-4]\d|50|51)\D[^(?:th|%|.,;)]*?quantitative',
            r'(?:^|\D)([3-4]\d|50|51)\D[^(?:th|%)]*?minimum[^.,;]*?quantitative',
            r'(?:^|\D)([3-4]\d|50|51)\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?quantitative',
            r'(?:above|below|no.*?(?:less|lower) than|higher|(?:at least))[^.,;]*?\D([3-4]\d|50|51)\D[^(?:th|%|.,;)]*?quantitative'
        ]
        self.gmat_aw = [
            r'(?:gmat|(?:graduate management admission test)).*?writing.*?minimum\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\b|[^(?:\d|th|%)]',
            r'(?:gmat|(?:graduate management admission test)).*?writing.*?(?:above|below|no.*?(?:less|lower) than|higher|at least)\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\b|[^(?:\d|th|%)]',
            r'(?:gmat|(?:graduate management admission test)).*?writing\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'(?:gmat|(?:graduate management admission test))\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%)]*?writing.*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'(?:gmat|(?:graduate management admission test)).*?minimum.*?writing\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\b|[^(?:\d|th|%)]',
            r'(?:gmat|(?:graduate management admission test)).*?(?:above|below|no.*?(?:less|lower) than|higher|at least).*?writing\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\b|[^(?:\d|th|%)]',            
            r'(?:gmat|(?:graduate management admission test)).*?minimum\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%|.,;)]*?writing',
            r'(?:gmat|(?:graduate management admission test))\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%)]*?minimum.*?writing',
            r'(?:gmat|(?:graduate management admission test))\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least).*?writing',
            r'(?:gmat|(?:graduate management admission test)).*?(?:above|below|no.*?(?:less|lower) than|higher|at least)\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%|.,;)]*?writing'
        ]
        self.gmat_code = [
            r'((?:university|institution|college|school)[^.,]*?code.*?(?:\d|[A-Z]){3}-(?:\d|[A-Z]){2}-(?:\d|[A-Z]){2}.*?(?:\)|\.))'
        ]
        self.bool_gmatgre = [
            r'((?:GRE|(?:graduate record exam)).*?or.*?(?:GMAT|(?:graduate management admission test)))',
            r'((?:GMAT|(?:graduate management admission test)).*?or.*?(?:GRE|(?:graduate record exam)))',
            r'((?:GMAT|(?:graduate management admission test))/(?:GRE|(?:graduate record exam)))',
            r'((?:GRE|(?:graduate record exam))/(?:GMAT|(?:graduate management admission test)))'
        ]
        self.enum_gmat = {
            "not_required":[
                r'((?:\s|GMAT|(?:graduate management admission test)) (?:not|\'t).*?require)',
                r'((?:not|\'t) require.*?(?:\s|GMAT|(?:graduate management admission test)))'
            ],
            "required":[
                r'((?:GMAT|(?:graduate management admission test))[^t]*?require[^(?:GRE|graduate record exam|LSAT|(?:law school admission test)|mcat)]*?)',
                r'([^t]*?require.*?(?:GMAT|(?:graduate management admission test))[^(?:GRE|graduate record exam|LSAT|(?:law school admission test)|mcat)]*?)'
            ],
            "optional":[
                r'((?:GMAT|(?:graduate management admission test)).*?(?:t require|recommend|optional|suggest|advise))',
                r'((?:t require|recommend|optional|suggest|advise).*?(?:GMAT|(?:graduate management admission test)))'
            ],
            "required_but_replaceable":[
                r'((?:GRE|(?:graduate record exam)).*?or.*?(?:GMAT|(?:graduate management admission test)))',
                r'((?:GMAT|(?:graduate management admission test)).*?or.*?(?:GRE|(?:graduate record exam)))',
                r'((?:GMAT|(?:graduate management admission test))/(?:GRE|(?:graduate record exam)))',
                r'((?:GRE|(?:graduate record exam))/(?:GMAT|(?:graduate management admission test)))'
            ],
            "not_clear":[
                
            ]
        }
        # gre 正则表达式
        self.gre_total = [
            r'(?:GRE|(?:graduate record exam))\D.*?((?:2[6-9]\d)|(?:3[0-4]\d))(?:\D|$)*?(?:\s|minimum|overall|total)',
            r'(?:GRE|(?:graduate record exam)).*?(?:\s|minimum|overall|total)\D.*?((?:2[6-9]\d)|(?:3[0-4]\d))(?:\D|$)',
            r'(?:^|\D)((?:2[6-9]\d)|(?:3[0-4]\d))\D.*?(?:GRE|(?:graduate record exam)).*?(?:\s|minimum|overall|total)',
            r'(?:^|\D)((?:2[6-9]\d)|(?:3[0-4]\d))\D.*?(?:\s|minimum|overall|total).*?(?:GRE|(?:graduate record exam))',
            r'(?:minimum|overall|total).*?(?:GRE|(?:graduate record exam))\D.*?((?:2[6-9]\d)|(?:3[0-4]\d))(?:\D|$)',
            r'(?:minimum|overall|total)\D.*?((?:2[6-9]\d)|(?:3[0-4]\d))\D.*?(?:GRE|(?:graduate record exam))'     
        ]
        self.gre_verbal = [
            r'verbal[^.,;]*?minimum[^.,;]*?\D(1[3-6]\d|170)\b|[^(?:\d|th|%)]',
            r'verbal[^.,;]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?\D(1[3-6]\d|170)\b|[^(?:\d|th|%)]',
            r'verbal[^.,;]*?\D(1[3-6]\d|170)\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'(?:^|\D)(1[3-6]\d|170)\D[^(?:th|%)]*?verbal[^.,;]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'minimum.*?verbal[^.,;]*?\D(1[3-6]\d|170)\b|[^(?:\d|th|%)]',
            r'(?:above|below|no.*?(?:less|lower) than|higher|at least).*?verbal[^.,;]*?\D(1[3-6]\d|170)\b|[^(?:\d|th|%)]',            
            r'minimum[^.,;]*?\D(1[3-6]\d|170)\D[^(?:th|%|.,;)]*?verbal',
            r'(?:^|\D)(1[3-6]\d|170)\D[^(?:th|%)]*?minimum[^.,;]*?verbal',
            r'(?:^|\D)(1[3-6]\d|170)\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?verbal',
            r'(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?\D(1[3-6]\d|170)\D[^(?:th|%|.,;)]*?verbal'
        ]
        self.gre_quantitative = [
            r'quantitative[^.,;]*?minimum[^.,;]*?\D(1[3-6]\d|170)\b|[^(?:\d|th|%)]',
            r'quantitative[^.,;]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?\D(1[3-6]\d|170)\b|[^(?:\d|th|%)]',
            r'quantitative[^.,;]*?\D(1[3-6]\d|170)\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'(?:^|\D)(1[3-6]\d|170)\D[^(?:th|%)]*?quantitative[^.,;]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'minimum.*?quantitative[^.,;]*?\D(1[3-6]\d|170)\b|[^(?:\d|th|%)]',
            r'(?:above|below|no.*?(?:less|lower) than|higher|at least).*?quantitative[^.,;]*?\D(1[3-6]\d|170)\b|[^(?:\d|th|%)]',            
            r'minimum[^.,;]*?\D(1[3-6]\d|170)\D[^(?:th|%|.,;)]*?quantitative',
            r'(?:^|\D)(1[3-6]\d|170)\D[^(?:th|%)]*?minimum[^.,;]*?quantitative',
            r'(?:^|\D)(1[3-6]\d|170)\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)[^.,;]*?quantitative',
            r'(?:above|below|no.*?(?:less|lower) than|higher|(?:at least))[^.,;]*?\D(1[3-6]\d|170)\D[^(?:th|%|.,;)]*?quantitative'
        ]
        self.gre_aw = [
            r'(?:GRE|(?:graduate record exam)).*?writing.*?minimum\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\b|[^(?:\d|th|%)]',
            r'(?:GRE|(?:graduate record exam)).*?writing.*?(?:above|below|no.*?(?:less|lower) than|higher|at least)\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\b|[^(?:\d|th|%)]',
            r'(?:GRE|(?:graduate record exam)).*?writing\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'(?:GRE|(?:graduate record exam))\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%)]*?writing.*?(?:above|below|no.*?(?:less|lower) than|higher|at least)',
            r'(?:GRE|(?:graduate record exam)).*?minimum.*?writing\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\b|[^(?:\d|th|%)]',
            r'(?:GRE|(?:graduate record exam)).*?(?:above|below|no.*?(?:less|lower) than|higher|at least).*?writing\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\b|[^(?:\d|th|%)]',            
            r'(?:GRE|(?:graduate record exam)).*?minimum\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%|.,;)]*?writing',
            r'(?:GRE|(?:graduate record exam))\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%)]*?minimum.*?writing',
            r'(?:GRE|(?:graduate record exam))\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%)]*?(?:above|below|no.*?(?:less|lower) than|higher|at least).*?writing',
            r'(?:GRE|(?:graduate record exam)).*?(?:above|below|no.*?(?:less|lower) than|higher|at least)\D.*?((?:[3-6](?:\)|\.)(?:0|5))|[3-6])\D[^(?:th|%|.,;)]*?writing'
        ]
        self.gre_code = [
            r'((?:university|institution|college|school)[^.,]*?code.*?\d{4}.*?(?:\)|\.))'
        ]
        self.enum_gre = {
            "not_required":[
                r'((?:\s|GRE|(?:graduate record exam)).*?(?:not|\'t) require)',
                r'((?:not|\'t) require.*?(?:\s|GRE|(?:graduate record exam)))'
            ],
            "required":[
                r'((?:GRE|(?:graduate record exam))[^t]*?require[^(?:GMAT|(?:graduate management admission test)|LSAT|(?:law school admission test)|mcat)]*?)',
                r'([^t]*?require.*?(?:GRE|(?:graduate record exam))[^(?:GMAT|(?:graduate management admission test)|LSAT|(?:law school admission test)|mcat)]*?)'
            ],
            "optional":[
                r'((?:GRE|(?:graduate record exam)).*?(?:t require|recommend|optional|suggest|advise))',
                r'((?:t require|recommend|optional|suggest|advise).*?(?:GRE|(?:graduate record exam)))'
            ],
            "required_but_replaceable":[
                r'((?:GRE|(?:graduate record exam)).*?or.*?(?:GMAT|(?:graduate management admission test)))',
                r'((?:GMAT|(?:graduate management admission test)).*?or.*?(?:GRE|(?:graduate record exam)))',
                r'((?:GRE|(?:graduate record exam))/(?:GMAT|(?:graduate management admission test)))',
                r'((?:GMAT|(?:graduate management admission test))/(?:GRE|(?:graduate record exam)))'
            ],
            "not_clear":[
                
            ]
        }
        self.gre_sub = [
            r'(GRE.*?(?:Subject exam|test).*?(?:\)|\.))',
            r'((?:Subject exam|test).*?GRE.*?(?:\)|\.))'
        ]


class InitData(RegExp):
    def __init__(self, file_path):
        super(InitData, self).__init__()

        # excle文件名
        self.file = file_path
        
        self.data = self._return_data()

        # 设置每一个需要提取出来的内容，及其对应的正则变量
        self.toefl = {
            'TOEFL Total': self.toefl_total,
            'TOEFL Reading': self.toefl_read,
            'TOEFL Listening': self.toefl_listen,
            'TOEFL Speaking': self.toefl_speak,
            'TOEFL Writing': self.toefl_write,
            'TOEFL code': self.toefl_code,
            'bool_TOEFL & IELTS是否同时接收？': self.bool_toeflielts, 
        }

        self.ielts = {
            # 'IELTS Total': self.ielts_total,
            #     'IELTS Reading': self.ielts_read,
            #     'IELTS Listening': self.ielts_listen,
            #     'IELTS Speaking': self.ielts_speak,
            #     'IELTS Writing': self.ielts_write,
        }

        self.gmat = {
            # 'GMAT total': self.gmat_total,
            # 'GMAT verbal': self.gmat_verbal,
            # 'GMAT quantitative': self.gmat_quantitative,
            # 'GMAT AW': self.gmat_aw,
            # 'GMAT code': self.gmat_code,
            # 'bool_GRE & GMAT是否同时接收？': self.bool_gmatgre,
            # 'enum_GMAT是否需要': self.enum_gmat,
        }

        self.gre = {
            # 'GRE total': self.gre_total,
            # 'GRE verbal': self.gre_verbal,
            # 'GRE quantitative': self.gre_quantitative,
            # 'GRE AW': self.gre_aw,
            # 'GRE code': self.gre_code,
            # 'enum_GRE是否需要': self.enum_gre,
            # 'GRE sub 要求': self.gre_sub
        }

        self.columns_mapping = {
            'TOEFL考试的具体要求（必填）': self.toefl,
            # 'IELTS考试的具体要求（必填）': self.ielts,
            # 'GMAT考试的具体分数要求': self.gmat,
            # 'GRE考试的具体分数要求（必填）': self.gre,
        }

    def _return_data(self):
        return pd.read_excel(self.file)


class ColumnsData(InitData):
    def __init__(self, content):
        self.content = content

    def apply_reg(self, grade, regs):
        st = ''
        if 'bool' in grade:
            for reg in regs:
                if st != '': return st
                pattern = re.compile(reg, re.IGNORECASE)
                r = re.findall(pattern, self.content)
                if pd.notnull(self.content):
                    for _ in r:
                        if _ != '':
                            st = '="true"'

        elif 'enum' in grade:
            for enums, reg in regs.items():
                if st != '': return st
                pattern = re.compile(reg, re.IGNORECASE)
                r = re.findall(pattern, self.content)
                if pd.notnull(self.content):
                    for _ in r:
                        if _ != '':
                            st = enums
        
        else:
            for reg in regs:
                if st != '': return st
                pattern = re.compile(reg, re.IGNORECASE)
                if pd.notnull(self.content):
                    r = re.findall(pattern, self.content)
                    for _ in r:
                        if _ != '':
                            try: st = float(_)
                            except: st = str(_)

        return st

class GradeExtract(InitData):
    def __init__(self, file_path):
        super(GradeExtract, self).__init__(file_path)
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'}
        self.result = []

    def _return_main_text(self):
        for columns in self.columns_mapping.keys():
            if columns not in self.data.columns:
                print("%s not in excel columns's name"% columns)
                sys.exit(0)

        return self.data[list(self.columns_mapping.keys())]

    def reuests_content(self, url):
        content = requests.get(url, headers=self.headers).text
        content = re.sub('[\n\r\t]', ' ', content)
        content = re.sub('<.*?>', ' ', content)
        content = re.sub('[ ]{2,}', ' ', content)
        return content

    def main_offline(self):
        data_list = self._return_main_text()
        total = len(data_list)
        num = 0
        for _, data in data_list.iterrows():
            num += 1
            self.show_schedule(total, num)
            res = []
            col = []
            for columns in self.columns_mapping.keys():
                col.append(columns)
                res.append(data[columns])
                for grade, regs in self.columns_mapping[columns].items():
                    col.append(grade)
                    res.append(ColumnsData(data[columns]).apply_reg(grade, regs))
            self.result.append(res)

        pd.DataFrame(self.result, columns=col).to_excel('result_offline.xlsx', index=False)

    def main_online(self):
        total = len(self.data)
        num = 0
        for data in self.data.values:
            num += 1
            self.show_schedule(total, num)
            res = list(data)
            col = list(self.data.columns)
            for grade_dict in self.columns_mapping.values():
                for grade, regs in grade_dict.items():
                    col.append(grade)
                    for url, col_ in zip(list(data)[1:], col[1:]):
                        if pd.isnull(url): continue
                        content = self.reuests_content(url)
                        st = ColumnsData(content).apply_reg(grade, regs)
                        if st != '':
                            res.append(st)
                            col.append('提取网址')
                            res.append(col_)
                            break
                    if st == '':
                        res.append(st)
                        col.append('提取网址')
                        res.append('')
            self.result.append(res)

        pd.DataFrame(self.result, columns=col).to_excel('result_online.xlsx', index=False)

    def show_schedule(self, total, num):
        sys.stdout.write('\r进度：{}|{}'.format('|'*int(num/total*100), str(num/total*100)[:5] + '%'))

while True:
    print('1、线下文本提取模式')
    print('2、线上爬虫提取模式')
    choose = input('请选择提取模式，按q退出： ')
    if choose == '1':
        print('你选择了线下文本提取模式，请保证托入文件的格式，满足程序要求！')
        file_path = input('请拖入文本: ')
        print('')
        go = GradeExtract(file_path)
        go.main_offline()

    elif choose == '2':
        print('你选择了线上爬虫提取模式，请保证托入文件的格式，满足程序要求！')
        file_path = input('请拖入文本: ')
        print('')
        go = GradeExtract(file_path)
        go.main_online()

    elif choose == 'q' or choose == 'Q':
        break

    else:
        print('错误输入！请输入1、2')
    print('\n')
