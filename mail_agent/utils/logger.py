#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Logger Setup
"""
import logging
import json
from pathlib import Path
from datetime import datetime

class N2KLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Load config
        config_path = Path(__file__).parent.parent / 'config' / 'mail_config.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        log_config = config.get('logging', {})
        
        # Setup logger
        self.logger = logging.getLogger('n2k_mail_agent')
        self.logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # File handler
        log_file = log_config.get('file', 'logs/mail_agent.log')
        log_path = Path(__file__).parent.parent / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(fh)
        
        # Console handler
        if log_config.get('console', True):
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%H:%M:%S'
            ))
            self.logger.addHandler(ch)
        
        self._initialized = True
    
    def get_logger(self):
        return self.logger

# Global logger instance
def get_logger():
    return N2KLogger().get_logger()
