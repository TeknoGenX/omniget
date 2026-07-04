import urllib.parse
import socket
import ipaddress
import requests

def is_safe_url(url):
    """
    Validate that the URL scheme is http/https and does not resolve
    to loopback, private, link-local, or multicast IP addresses (SSRF Protection).
    """
    if not url:
        return False
        
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
            
        hostname = parsed.hostname
        if not hostname:
            return False
            
        # Resolve hostname to all associated IPs (supports IPv4 and IPv6)
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip)
            if (ip_obj.is_private or 
                ip_obj.is_loopback or 
                ip_obj.is_link_local or 
                ip_obj.is_multicast):
                return False
                
        return True
    except Exception:
        return False

def safe_requests_get(url, **kwargs):
    """
    HTTP GET request wrapper that manually validates redirects to prevent SSRF bypass.
    """
    # Force disable automatic redirects
    kwargs['allow_redirects'] = False
    
    max_redirects = 5
    current_url = url
    
    for _ in range(max_redirects):
        if not is_safe_url(current_url):
            raise requests.exceptions.RequestException(f"SSRF Protection: Blocked request to unsafe URL: {current_url}")
            
        response = requests.get(current_url, **kwargs)
        
        # Check for redirect status codes (301, 302, 303, 307, 308)
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location')
            if not redirect_url:
                break
            # Resolve relative redirect URLs
            current_url = urllib.parse.urljoin(current_url, redirect_url)
        else:
            return response
            
    raise requests.exceptions.TooManyRedirects("Exceeded maximum redirects allowed under SSRF protection.")

def safe_requests_head(url, **kwargs):
    """
    HTTP HEAD request wrapper that manually validates redirects to prevent SSRF bypass.
    """
    # Force disable automatic redirects
    kwargs['allow_redirects'] = False
    
    max_redirects = 5
    current_url = url
    
    for _ in range(max_redirects):
        if not is_safe_url(current_url):
            raise requests.exceptions.RequestException(f"SSRF Protection: Blocked request to unsafe URL: {current_url}")
            
        response = requests.head(current_url, **kwargs)
        
        # Check for redirect status codes (301, 302, 303, 307, 308)
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location')
            if not redirect_url:
                break
            # Resolve relative redirect URLs
            current_url = urllib.parse.urljoin(current_url, redirect_url)
        else:
            return response
            
    raise requests.exceptions.TooManyRedirects("Exceeded maximum redirects allowed under SSRF protection.")
