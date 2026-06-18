#!/usr/bin/env python3
"""Extract message structure from Telegram HTML export for analysis."""
import re, sys, json
from html.parser import HTMLParser
from collections import defaultdict
from datetime import datetime

class MsgExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.in_text = False
        self.in_from = False
        self.in_service = False
        self.current = {}
        self.text_buf = []
        self.from_buf = []
        self.date = ""
        self.time = ""
        self.skip_tags = {'a','b','i','u','s','code','pre','strong','em','span'}
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'div':
            cls = attrs_dict.get('class','')
            if 'service' in cls:
                self.in_service = True
            elif 'text' in cls:
                self.in_text = True
                self.text_buf = []
            elif 'from_name' in cls:
                self.in_from = True
                self.from_buf = []
            elif 'pull_right date' in cls:
                title = attrs_dict.get('title','')
                m = re.search(r'(\d+)\.(\d+)\.(\d{4}) (\d+):(\d+)', title)
                if m:
                    self.current['timestamp'] = f"{m.group(3)}-{m.group(2)}-{m.group(1)} {m.group(4)}:{m.group(5)}"
        elif tag == 'a' and self.in_service:
            onclick = attrs_dict.get('onclick','')
            if 'ShowBotCommand' in onclick or 'sendMessage' in onclick:
                m = re.search(r'"([^"]+)"', onclick)
                if m:
                    self.current['command'] = m.group(1)
    
    def handle_endtag(self, tag):
        if tag == 'div' and self.in_text:
            self.in_text = False
            t = ''.join(self.text_buf).strip()
            if t:
                self.current['text'] = t
        elif tag == 'div' and self.in_from:
            self.in_from = False
            self.current['from'] = ''.join(self.from_buf).strip()
        elif tag == 'div' and self.in_service:
            self.in_service = False
            svc = ''.join(self.text_buf).strip()
            if svc:
                self.current['service'] = svc
    
    def handle_data(self, data):
        if self.in_text:
            self.text_buf.append(data)
        elif self.in_from:
            self.from_buf.append(data)
    
    def handle_entityref(self, name):
        c = {'amp':'&','lt':'<','gt':'>','quot':'"','#39':"'"}.get(name, f'&{name};')
        if self.in_text:
            self.text_buf.append(c)
        elif self.in_from:
            self.from_buf.append(c)

def extract_structured(filepath, skip_truncated=True):
    """Extract structured messages, filtering out truncated/excessive empties."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Remove script blocks to avoid parsing JS as HTML
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    extractor = MsgExtractor()
    extractor.feed(html)
    
    # Filter: only keep non-empty, substantive messages
    substantial = []
    for m in extractor.messages:
        # Keep if it has text content
        if m.get('text','').strip() and len(m['text'].strip()) > 3:
            substantial.append(m)
        # Or if it's a user command
        elif m.get('command'):
            substantial.append(m)
        # Or if it's a date marker
        elif m.get('service'):
            substantial.append(m)
    
    return substantial

if __name__ == '__main__':
    # Extract category summaries from each file
    base = "/Users/peterqiu/Downloads/Telegram Desktop/ChatExport_2026-05-04 (2)"
    files = ['messages.html', 'messages2.html', 'messages3.html']
    
    for fname in files:
        path = f"{base}/{fname}"
        msgs = extract_structured(path)
        print(f"\n{'='*60}")
        print(f"=== {fname}: {len(msgs)} substantial messages ===")
        print('='*60)
        
        # Show first 5 and last 3 with context
        for i, m in enumerate(msgs[:8]):
            text = m.get('text','')[:150]
            ts = m.get('timestamp','')
            sender = m.get('from','')
            print(f"  [{ts}] {sender}: {text}")
            if m.get('command'):
                print(f"    → command: {m['command']}")
        print(f"  ... ({len(msgs)-11} messages in between) ...")
        for i, m in enumerate(msgs[-3:]):
            text = m.get('text','')[:150]
            ts = m.get('timestamp','')
            sender = m.get('from','')
            print(f"  [{ts}] {sender}: {text}")
            if m.get('service'):    
                print(f"    → service: {m['service']}")
