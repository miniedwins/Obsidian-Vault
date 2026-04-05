import os
import re
import argparse
import sys
from opencc import OpenCC
from deep_translator import GoogleTranslator

# Technical terms to protect from translation
PROTECTED_TERMS = [
    r'AI', r'RAG', r'Agent', r'CLI', r'SDK', r'GPT', r'LLM', r'API', r'UI', r'UX',
    r'v\d+(\.\d+)*', r'\d{4}-\d{2}-\d{2}', r'\d{8}'
]

class LocalizerEngine:
    def __init__(self, mode='auto'):
        self.mode = mode
        self.cc = OpenCC('s2twp')
        self.translator = GoogleTranslator(source='auto', target='zh-TW')
        self.term_map = {}

    def has_japanese_kana(self, text):
        return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text))

    def has_simplified_chinese(self, text):
        # A simple check: if CC conversion changes the text, it likely had simplified chars
        converted = self.cc.convert(text)
        return converted != text

    def protect_terms(self, text):
        self.term_map = {}
        def replace(match):
            placeholder = f"__TERM_{len(self.term_map)}__"
            self.term_map[placeholder] = match.group(0)
            return placeholder
        
        pattern = '|'.join(f'({p})' for p in PROTECTED_TERMS)
        return re.sub(pattern, replace, text, flags=re.IGNORECASE)

    def restore_terms(self, text):
        for placeholder, original in self.term_map.items():
            text = text.replace(placeholder, original)
        return text

    def process_text(self, text):
        if not text: return text
        
        # Protect terms before any processing
        protected_text = self.protect_terms(text)
        
        result = protected_text
        
        if self.mode == 's2t':
            # Only convert if it has simplified Chinese
            result = self.cc.convert(protected_text)
        else: # auto mode
            if self.has_japanese_kana(protected_text):
                try:
                    # For filenames with prefixes (e.g., ID_Text)
                    match = re.match(r'^([a-zA-Z0-9]+_)(.*)$', protected_text)
                    if match:
                        prefix, rest = match.groups()
                        result = prefix + self.translator.translate(rest)
                    else:
                        result = self.translator.translate(protected_text)
                except:
                    result = self.cc.convert(protected_text)
            elif self.has_simplified_chinese(protected_text):
                result = self.cc.convert(protected_text)
            else:
                # If it's mostly English with spaces/underscores, translate it
                if ' ' in protected_text or '_' in protected_text:
                    try:
                        result = self.translator.translate(protected_text)
                    except:
                        pass

        # Restore protected terms
        final_text = self.restore_terms(result)
        # Clean invalid Windows characters
        final_text = re.sub(r'[\\/*?:"<>|]', "", final_text)
        return final_text.strip()

def main():
    parser = argparse.ArgumentParser(description='Traditional Chinese Filename Localizer')
    parser.add_argument('--dir', required=True, help='Directory to scan')
    parser.add_argument('--ext', help='File extension to filter (e.g. .mp4)')
    parser.add_argument('--mode', choices=['auto', 's2t'], default='auto', help='Conversion mode')
    parser.add_argument('--preview', action='store_true', help='Preview changes without applying')
    parser.add_argument('--apply', action='store_true', help='Apply changes to files')

    args = parser.parse_args()
    
    if not args.preview and not args.apply:
        print("Error: Specify either --preview or --apply")
        sys.exit(1)

    engine = LocalizerEngine(mode=args.mode)
    root_dir = args.dir
    target_ext = args.ext.lower() if args.ext else None
    
    changes = []
    
    # Scan files
    for filename in os.listdir(root_dir):
        old_path = os.path.join(root_dir, filename)
        if not os.path.isfile(old_path):
            continue
            
        name, ext = os.path.splitext(filename)
        
        # Filter by extension
        if target_ext and ext.lower() != target_ext:
            continue
            
        new_name_base = engine.process_text(name)
        new_filename = new_name_base + ext
        
        if new_filename != filename:
            changes.append((filename, new_filename))

    if not changes:
        print("No files need renaming.")
        return

    if args.preview:
        print("\n### 檔案更名預覽清單 (Preview)")
        print("| 原始檔名 | 建議新檔名 |")
        print("| :--- | :--- |")
        for old, new in changes:
            print(f"| {old} | {new} |")
        print(f"\n總共偵測到 {len(changes)} 個檔案需要更名。")
    
    if args.apply:
        success_count = 0
        fail_count = 0
        for old, new in changes:
            old_path = os.path.join(root_dir, old)
            new_path = os.path.join(root_dir, new)
            
            # Collision handling
            if os.path.exists(new_path) and old.lower() != new.lower():
                base, ext = os.path.splitext(new)
                counter = 1
                while os.path.exists(os.path.join(root_dir, f"{base}_{counter}{ext}")):
                    counter += 1
                new = f"{base}_{counter}{ext}"
                new_path = os.path.join(root_dir, new)
            
            try:
                os.rename(old_path, new_path)
                success_count += 1
            except Exception as e:
                print(f"Failed to rename {old}: {e}")
                fail_count += 1
        
        print(f"\n執行完成！成功: {success_count}, 失敗: {fail_count}")

if __name__ == "__main__":
    main()
