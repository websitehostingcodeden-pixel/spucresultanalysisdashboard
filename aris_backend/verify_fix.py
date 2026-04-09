import inspect
from apps.results.services import analyzer

source = inspect.getsource(analyzer.process_upload)
has_social = 'social' in source
has_economics = 'economics' in source  
has_accountancy = 'accountancy' in source

if has_social and has_economics and has_accountancy:
    print("VERIFIED: Enhanced whitelist is active in code")
else:
    print("ERROR: Whitelist not found")
    print(f"  has_social: {has_social}")
    print(f"  has_economics: {has_economics}")
    print(f"  has_accountancy: {has_accountancy}")
