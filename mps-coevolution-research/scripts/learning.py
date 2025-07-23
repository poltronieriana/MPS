'''import requests

def search_repositories_mbeddr():

    url = "https://api.github.com/search/repositories"

    search = "mbeddr"
    quantity = 5

    params = {
            'q': search, 
            "per page": quantity,
        }
  
    response = requests.get(url, params=params)

    if response.status_code == 200:
            data = response.json()
            
    for repo in data['items']:
                name = repo['name']           
                owner = repo['owner']['login']    
                description = repo.get('description', 'Sem descrição')
                
                print(f"  Name: {name}")
                print(f"     Owner: {owner}")
                print(f"     Description: {description}")
                print("     ---")
        
    else:
            print(f" Error: {response.status_code}")

    for item in data['items']:
        print(f"Repo: {item['name']}")
        print(f"Owner: {item['owner']['login']}")
        print("---")
        
    print("Total encontrado:", data['total_count'])
    print("first respository:", data['items'][0]['name'])


def search_model_mbeddr():
    url = "https://api.github.com/search/repositories"
    quantity = 3
    
    queries = [
        "mbeddr language:mps",          
        "mbeddr extension:mpr",         
        "com.mbeddr.core in:file",       
    ]
    
    for query in queries:
        print(f"\n  Buscando: '{query}'")
                
        params = {
        
            'q': query, 
            'per_page': quantity,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"Encontrados: {data['total_count']}")
            print (f"Repo Name: {data['items'][0]['name']}")
            print (f"Owner: {data['items'][0]['owner']['login']}")
            print (f"Description: {data['items'][0].get('description', 'Sem descrição')}")            
            print("-----")
            for item in data['items']:
                print(f"Repo: {item['name']}")
                print(f"Owner: {item['owner']['login']}")
                print(f"Description: {item.get('description', 'Sem descrição')}")
                print("---")
        
    else:
            print(f" Error: {response.status_code}")        

search_model_mbeddr()

def analisar_um_repositorio(owner, repo_name):
    """Analisa UM repositório específico"""
    print(f"\nAnalisando: {owner}/{repo_name}")
    
    repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    
    response = requests.get(repo_url)
    
    if response.status_code == 200:
        repo_data = response.json()
        
        tamanho = repo_data['size']  
        descricao = repo_data.get('description', 'Sem descrição')
        linguagem = repo_data.get('language', 'Não especificada')
        
        print(f"Tamanho: {tamanho} KB")
        print(f"Descrição: {descricao}")
        print(f"Linguagem: {linguagem}")
        
        if tamanho < 50000:  
            print("TAMANHO PEQUENO - possível modelo")
        else:
            print("TAMANHO GRANDE - possível metamodelo")
            
    else:
        print(f"Erro: {response.status_code}")

analisar_um_repositorio("diederikd", "MultiLingual")'''





'''º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚ºº˚º˚º˚º Serious Work º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º˚º'''


import requests  

def finding_mbeddr_models():
    url = "https://api.github.com/search/repositories"
    
    queries = [
        "mbeddr",                    
        "mbeddr.core", 
        "com.mbeddr", 
        "language:mps mbeddr", 
        "jetbrains mps embedded",
        "mbeddr language:mps",
        "mbeddr extension:mpr", 
        "com.mbeddr.core in:file",
    ]
    
    quantity = 10  
    
    for query in queries:
        print(f"Buscando: {query}")
        
        params = {
            "q": query,
            "per_page": quantity, 
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            for repo in data['items']:
                repo_name = repo['name']
                owner = repo['owner']['login']
                
                if is_potential_model_repo(owner, repo_name):
                    print(f"MODELO ENCONTRADO: {owner}/{repo_name}")

def is_potential_model_repo(owner, repo_name):  
    tree_url = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/HEAD?recursive=1"
    
    response = requests.get(tree_url)
    
    if response.status_code == 200:
        data = response.json()
        
        for item in data['tree']:
            path = item['path']
            
            if '/solutions/' in path and path.endswith('.mps'):
                return True
            elif '/examples/' in path and path.endswith('.mps'):
                return True
            elif '/tests/' in path and path.endswith('.mps'):
                return True
    
    return False

finding_mbeddr_models()  