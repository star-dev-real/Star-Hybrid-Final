# compile.py
import os
import sys
from PyInstaller.__main__ import run
from PyInstaller.utils.hooks import collect_all

def get_mitmproxy_dependencies():
    datas, binaries, hiddenimports = collect_all('mitmproxy')
    
    # Additional required imports
    extra_imports = [
        'mitmproxy.addons',
        'mitmproxy.tools.web',
        'mitmproxy.proxy.protocol.http',
        'mitmproxy.proxy.protocol.tls',
        'mitmproxy.certs',
        'cryptography.hazmat.backends.openssl',
        'ujson',
        'brotli',
        'zstandard'
    ]
    
    # Format data files correctly
    formatted_datas = [
        f"cosmetics_cache.json{os.pathsep}."
    ]
    
    # Format binary files
    formatted_binaries = []
    
    return formatted_datas, formatted_binaries, hiddenimports + extra_imports

if __name__ == '__main__':
    datas, binaries, hiddenimports = get_mitmproxy_dependencies()
   
    # Basic configuration options
    opts = [
        'test.py',      
        '--onefile',
        '--name=StarHybrid',
        '--noconsole',
        '--paths=' + os.pathsep.join(sys.path),
    ]
    
    # Add icon if exists
    if os.path.exists('icon.ico'):
        opts.append('--icon=icon.ico')
    
    # Add OpenSSL binary if exists
    openssl_dll = 'libcrypto-1_1.dll'
    if os.path.exists(openssl_dll):
        opts.append(f'--add-binary={openssl_dll};.')
    
    # Add data files
    for data in datas:
        opts.append(f'--add-data={data}')
    
    # Add binary files
    for binary in binaries:
        opts.append(f'--add-binary={binary}')
    
    # Add hidden imports
    for imp in hiddenimports:
        opts.append(f'--hidden-import={imp}')
    
    try:
        run(opts)
        print("\nCompilation successful! Find your executable in the 'dist' folder.")
        print("IMPORTANT: Users must install mitmproxy's CA certificate for HTTPS interception.")
    except Exception as e:
        print(f"\nCompilation failed: {str(e)}")
        print("Common solutions:")
        print("1. Make sure all required files exist (cosmetics_cache.json, icon.ico)")
        print("2. Run as administrator if you get permission errors")
        print("3. Try without --onefile if you get size-related errors")