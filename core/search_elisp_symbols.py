#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 Andy Stewart
# 
# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: <lazycat.manatee@gmail.com> <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import functools
import threading
import os
import traceback
import sexpdata
import re

from core.utils import get_emacs_vars, message_emacs, eval_in_emacs, logger


class SearchElispSymbols:
    
    def __init__(self) -> None:
        self.search_ticker = 0
        self.search_thread_queue = []
        self.search_max_number = 300
        self.symbols = []
        
    def update(self, symbols):
        self.symbols = sorted(list(map(str, symbols)), key=len)
        
    def search(self, prefix: str):
        ticker = self.search_ticker + 1
        self.search_ticker = ticker
        
        search_thread = threading.Thread(target=lambda: self.search_symbols(prefix, ticker))
        search_thread.start()
        self.search_thread_queue.append(search_thread)
        
    def match_symbol(self, prefix, prefix_regexp, symbol):
        return symbol.startswith(prefix) or symbol.replace("-", "").startswith(prefix) or prefix_regexp.match(symbol)
        
    def sort_symbols(self, prefix, symbol_a, symbol_b):
        symbol_a_starts_with_prefix = symbol_a.startswith(prefix)
        symbol_b_starts_with_prefix = symbol_b.startswith(prefix)
        
        if symbol_a_starts_with_prefix and symbol_b_starts_with_prefix:
            return len(symbol_a) < len(symbol_b)
        elif symbol_a_starts_with_prefix:
            return -1
        elif symbol_b_starts_with_prefix:
            return 1
        else: 
            return len(symbol_a) < len(symbol_b)
    
    def search_symbols(self, prefix: str, ticker: int):
        candidates = []
        prefix_regexp = re.compile(re.sub(r'([a-zA-Z0-9-_])', r'\1.*', re.escape(prefix)))
        for symbol in self.symbols:
            if self.match_symbol(prefix, prefix_regexp, symbol):
                candidates.append(symbol)
                    
                if len(candidates) > self.search_max_number:
                    break
                
        if ticker == self.search_ticker:
            eval_in_emacs("lsp-bridge-search-elisp-symbols--record-items", 
                          sorted(candidates, key=functools.cmp_to_key(lambda a, b: self.sort_symbols(prefix, a, b))))
