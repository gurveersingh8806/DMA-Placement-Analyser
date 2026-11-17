for name in ['fitz','pdf2image','PIL']:
 try:
  m=__import__(name); print(name, 'available')
 except Exception as e: print(name, 'missing')
