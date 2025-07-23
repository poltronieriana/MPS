#!/usr/bin/env python3
"""
Script para descobrir e analisar modelos do mbeddr no JetBrains MPS
Criado para pesquisa sobre co-evolução de metamodelos e modelos

Autor: Ana Carolina Poltronieri
Universidade: Unipampa
Projeto: Collecting metamodel/model data from JetBrains MPS
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter
import argparse
from datetime import datetime

class MbeddrModelDiscovery:
    """Classe principal para descobrir modelos do mbeddr"""
    
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.models_found = []
        self.metamodels_found = []
        self.statistics = defaultdict(int)
        
        self.mps_extensions = {
            '.mps': 'MPS Model',
            '.mpl': 'MPS Language',
            '.msd': 'MPS Solution', 
            '.devkit': 'MPS DevKit',
            '.xml': 'MPS XML Model'
        }
        
        self.model_patterns = {
            'structure': r'structure\.mps$',
            'behavior': r'behavior\.mps$', 
            'editor': r'editor\.mps$',
            'generator': r'generator\.mps$',
            'typesystem': r'typesystem\.mps$',
            'constraints': r'constraints\.mps$'
        }
    
    def scan_repository(self):
        """Escaneia o repositório em busca de arquivos MPS"""
        print(f"🔍 Escaneando repositório: {self.repo_path}")
        print("=" * 60)
        
        if not self.repo_path.exists():
            print(f"Erro: Repositório não encontrado em {self.repo_path}")
            return
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                self.analyze_file(file_path)
        
        print(f"Escaneamento concluído!")
        print(f"Encontrados: {len(self.models_found)} modelos e {len(self.metamodels_found)} metamodelos")
    
    def analyze_file(self, file_path):
        """Analisa um arquivo individual"""
        file_ext = file_path.suffix.lower()
        
        if file_ext in self.mps_extensions:
            self.statistics['total_mps_files'] += 1
            
            file_type = self.classify_file_type(file_path)
            
            if file_type:
                model_info = {
                    'path': str(file_path),
                    'name': file_path.name,
                    'type': file_type,
                    'extension': file_ext,
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                }
                
                if self.is_metamodel(file_path, file_type):
                    self.metamodels_found.append(model_info)
                    self.statistics['metamodels'] += 1
                else:
                    self.models_found.append(model_info)
                    self.statistics['models'] += 1
                
                self.statistics[f'type_{file_type}'] += 1
    
    def classify_file_type(self, file_path):
        """Classifica o tipo do arquivo MPS"""
        file_name = file_path.name.lower()
        file_content = ""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read(1000) 
        except:
            pass
        
        for pattern_name, pattern in self.model_patterns.items():
            if re.search(pattern, file_name):
                return pattern_name
        
        if 'language=' in file_content or '<language' in file_content:
            return 'language_definition'
        elif 'model=' in file_content or '<model' in file_content:
            return 'model_instance'
        elif 'solution=' in file_content:
            return 'solution'
        elif 'devkit=' in file_content:
            return 'devkit'
        
        return 'unknown'
    
    def is_metamodel(self, file_path, file_type):
        """Determina se um arquivo é um metamodelo ou modelo"""
        path_str = str(file_path).lower()
        
        metamodel_indicators = [
            'structure',
            'behavior', 
            'editor',
            'generator',
            'typesystem',
            'constraints',
            'language',
            '/languages/',
            '/devkits/'
        ]
        
        return any(indicator in path_str for indicator in metamodel_indicators)
    
    def generate_statistics(self):
        """Gera estatísticas dos modelos encontrados"""
        print("\n ESTATÍSTICAS DETALHADAS")
        print("=" * 60)
        
        print(f"Total de arquivos MPS: {self.statistics['total_mps_files']}")
        print(f"Modelos encontrados: {self.statistics['models']}")
        print(f"Metamodelos encontrados: {self.statistics['metamodels']}")
        
        print("\nDistribuição por tipo:")
        type_counts = {k: v for k, v in self.statistics.items() if k.startswith('type_')}
        for type_name, count in sorted(type_counts.items()):
            clean_name = type_name.replace('type_', '').replace('_', ' ').title()
            print(f"  {clean_name}: {count}")
        
        if self.models_found or self.metamodels_found:
            all_files = self.models_found + self.metamodels_found
            recent_files = sorted(all_files, key=lambda x: x['modified'], reverse=True)[:5]
            
            print("\nArquivos modificados recentemente:")
            for file_info in recent_files:
                print(f"  {file_info['name']} - {file_info['modified'].strftime('%Y-%m-%d %H:%M')}")
    
    def export_results(self, output_file='mbeddr_models_analysis.json'):
        """Exporta os resultados para um arquivo JSON"""
        results = {
            'metadata': {
                'repository_path': str(self.repo_path),
                'scan_timestamp': datetime.now().isoformat(),
                'total_files_scanned': self.statistics['total_mps_files']
            },
            'statistics': dict(self.statistics),
            'models': self.models_found,
            'metamodels': self.metamodels_found
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\nResultados exportados para: {output_file}")
    
    def print_sample_findings(self, limit=5):
        """Imprime alguns exemplos dos achados"""
        print(f"\n EXEMPLOS DE MODELOS ENCONTRADOS (primeiros {limit}):")
        print("-" * 60)
        
        for i, model in enumerate(self.models_found[:limit]):
            print(f"{i+1}. {model['name']}")
            print(f"   Tipo: {model['type']}")
            print(f"   Caminho: {model['path']}")
            print(f"   Tamanho: {model['size']} bytes")
            print()
        
        print(f"\n  EXEMPLOS DE METAMODELOS ENCONTRADOS (primeiros {limit}):")
        print("-" * 60)
        
        for i, metamodel in enumerate(self.metamodels_found[:limit]):
            print(f"{i+1}. {metamodel['name']}")
            print(f"   Tipo: {metamodel['type']}")
            print(f"   Caminho: {metamodel['path']}")
            print(f"   Tamanho: {metamodel['size']} bytes")
            print()

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Descobre modelos do mbeddr no JetBrains MPS',
        epilog='Exemplo: python mbeddr_discovery.py /path/to/mbeddr.core'
    )
    
    parser.add_argument(
        'repo_path',
        help='Caminho para o repositório mbeddr.core'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='mbeddr_models_analysis.json',
        help='Arquivo de saída para os resultados (padrão: mbeddr_models_analysis.json)'
    )
    
    parser.add_argument(
        '--sample',
        type=int,
        default=5,
        help='Número de exemplos para mostrar (padrão: 5)'
    )
    
    args = parser.parse_args()
    
    print(" DESCOBRIDOR DE MODELOS MBEDDR")
    print("Projeto: Co-evolução de Metamodelos e Modelos em JetBrains MPS")
    print("Pesquisadora: Ana Carolina Poltronieri - Unipampa")
    print("=" * 60)
    
    discovery = MbeddrModelDiscovery(args.repo_path)
    discovery.scan_repository()
    discovery.generate_statistics()
    discovery.print_sample_findings(args.sample)
    discovery.export_results(args.output)
    
    print("\n✨ Análise concluída com sucesso!")

if __name__ == '__main__':
    main()