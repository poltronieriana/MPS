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

import time
import requests  
import json
from datetime import datetime

found_models = []

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
   
   quantity = 20
   total_models_found = 0
   
   for query in queries:
       print(f"Searching: {query}")
       
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
               description = repo.get('description') or 'No description`'                
               if is_potential_model_repo(owner, repo_name):  
                   stars = repo.get('stargazers_count', 0)
                   repo_url = repo['html_url']
                   
                   model_info = {
                       'owner': owner,
                       'name': repo_name,
                       'description': description,
                       'stars': stars,
                       'url': repo_url,
                       'found_at': datetime.now().isoformat()
                   }
                   found_models.append(model_info)
                   
                   print(f"  {owner}/{repo_name}")
                   print(f"     description: {description[:60]}...")
                   print(f"     Stars: {stars}")
                   print(f"     URL: {repo_url}")
                   print(f"     Model found")
                   print(" ˚º˚º˚º˚º˚º˚º˚")
                   total_models_found += 1
       
       time.sleep(1)
   
   print(f"\nTotal models found: {total_models_found}")
   return total_models_found

def is_potential_model_repo(owner, repo_name):
   tree_url = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/HEAD?recursive=1"
   
   response = requests.get(tree_url)
   
   if response.status_code == 200:
       data = response.json()
       
       has_solutions = False
       has_mps_files = False
       has_msd_files = False
       
       for item in data['tree']:
           path = item['path']
           
           if '/solutions/' in path and path.endswith('.mps'):
               has_solutions = True
               has_mps_files = True
               return True
           elif '/examples/' in path and path.endswith('.mps'):
               has_mps_files = True
               return True  
           elif '/tests/' in path and path.endswith('.mps'):
               has_mps_files = True
               return True
               
           if path.endswith('.msd'):
               has_msd_files = True
           if '/solutions/' in path:
               has_solutions = True
               
       if has_solutions and (has_msd_files or has_mps_files):
           return True
   
   return False

def remove_duplicates():
    global found_models
    seen = set()
    unique_models = []
    
    for model in found_models:
        repo_id = f"{model['owner']}/{model['name']}"
        if repo_id not in seen:
            seen.add(repo_id)
            unique_models.append(model)
    
    duplicates_removed = len(found_models) - len(unique_models)
    found_models = unique_models
    print(f"Removed {duplicates_removed} duplicates")

finding_mbeddr_models()

remove_duplicates()

print(f"\n º˚º˚ºTotal models found: {len(found_models)}˚º˚º˚º")

found_models.sort(key=lambda x: x['stars'], reverse=True)

print("\nBy star number:")
for i, model in enumerate(found_models[:5]):
   print(f"{i+1}. {model['owner']}/{model['name']} - {model['stars']} stars")

with open('mbeddr_models_found.json', 'w') as f:
   json.dump(found_models, f, indent=2)

