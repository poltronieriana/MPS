#!/usr/bin/env python3
"""
MPS Repository Analyzer - Análise de Co-evolução de Metamodelos
Autor: Ana Carolina Poltronieri
Propósito: Coletar dados sobre evolução de DSLs em repositórios MPS
"""

import os
import json
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

class MPSRepositoryAnalyzer:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.results = {
            'basic_metrics': {},
            'metamodel_changes': [],
            'contributors': {},
            'timeline': [],
            'breaking_changes': []
        }
    
    def run_git_command(self, command):
        """Executa comando git e retorna resultado"""
        try:
            result = subprocess.run(
                command, 
                cwd=self.repo_path, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Erro ao executar: {command}")
            return ""
    
    def analyze_basic_metrics(self):
        """Coleta métricas básicas do repositório"""
        print("Coletando métricas básicas")
        
        total_commits = self.run_git_command("git rev-list --count HEAD")
        
        first_commit = self.run_git_command("git log --reverse --format='%ci' | head -1")
        last_commit = self.run_git_command("git log --format='%ci' -1")
        
        contributors = self.run_git_command("git shortlog -sn --all")
        contributor_count = len(contributors.split('\n')) if contributors else 0
        
        mps_files = self.run_git_command("find . -name '*.mps' | wc -l")
        
        self.results['basic_metrics'] = {
            'total_commits': int(total_commits) if total_commits else 0,
            'first_commit_date': first_commit,
            'last_commit_date': last_commit,
            'contributor_count': contributor_count,
            'mps_files_count': int(mps_files) if mps_files else 0,
            'repository_age_days': self._calculate_repo_age(first_commit, last_commit)
        }
        
        return self.results['basic_metrics']
    
    def _calculate_repo_age(self, first_date, last_date):
        """Calcula idade do repositório em dias"""
        try:
            first = datetime.fromisoformat(first_date.replace(' +', '+'))
            last = datetime.fromisoformat(last_date.replace(' +', '+'))
            return (last - first).days
        except:
            return 0
    
    def analyze_metamodel_changes(self):
        """Analisa mudanças específicas em metamodelos"""
        print("Analisando mudanças em metamodelos...")
        
        structure_commits = self.run_git_command(
            "git log --oneline --name-only | grep -B1 'structure\\.mps' | grep '^[a-f0-9]'"
        )
        
        mps_commits = self.run_git_command(
            "git log --oneline --name-only | grep -B1 '\\.mps$' | grep '^[a-f0-9]'"
        )
        
        structure_commit_list = structure_commits.split('\n') if structure_commits else []
        
        for commit_hash in structure_commit_list[:20]:  
            if commit_hash:
                commit_info = self._analyze_commit(commit_hash)
                if commit_info:
                    self.results['metamodel_changes'].append(commit_info)
        
        self.results['metamodel_stats'] = {
            'structure_commits_count': len(structure_commit_list),
            'total_mps_commits': len(mps_commits.split('\n')) if mps_commits else 0
        }
        
        return self.results['metamodel_changes']
    
    def _analyze_commit(self, commit_hash):
        """Analisa um commit específico"""
        commit_msg = self.run_git_command(f"git log --format='%s' -1 {commit_hash}")
        commit_date = self.run_git_command(f"git log --format='%ci' -1 {commit_hash}")
        commit_author = self.run_git_command(f"git log --format='%an' -1 {commit_hash}")
        
        files_changed = self.run_git_command(f"git show --name-only --format='' {commit_hash}")
        
        change_type = self._classify_change_type(commit_msg, files_changed)
        
        return {
            'hash': commit_hash,
            'message': commit_msg,
            'date': commit_date,
            'author': commit_author,
            'files_changed': files_changed.split('\n') if files_changed else [],
            'change_type': change_type,
            'is_breaking': self._is_breaking_change(commit_msg)
        }
    
    def _classify_change_type(self, commit_msg, files_changed):
        """Classifica o tipo de mudança baseado na mensagem e arquivos"""
        msg_lower = commit_msg.lower()
        files_str = files_changed.lower()
        
        if 'structure.mps' in files_str:
            return 'structural'
        elif 'editor.mps' in files_str:
            return 'presentation'
        elif 'migration.mps' in files_str:
            return 'migration'
        elif any(keyword in msg_lower for keyword in ['add', 'new', 'create']):
            return 'addition'
        elif any(keyword in msg_lower for keyword in ['remove', 'delete', 'drop']):
            return 'removal'
        else:
            return 'modification'
    
    def _is_breaking_change(self, commit_msg):
        """Detecta se é uma mudança breaking"""
        breaking_keywords = [
            'break', 'breaking', 'remove', 'delete', 'drop',
            'migrate', 'migration', 'incompatible', 'deprecated'
        ]
        return any(keyword in commit_msg.lower() for keyword in breaking_keywords)
    
    def analyze_contributors(self):
        """Analisa padrões de contribuição"""
        print("Analisando contribuintes")
        
        contributors_raw = self.run_git_command("git shortlog -sn --all")
        
        yearly_activity = self.run_git_command(
            "git log --format='%ci' | cut -d'-' -f1 | sort | uniq -c"
        )
        
        self.results['contributors'] = {
            'top_contributors': contributors_raw.split('\n')[:10] if contributors_raw else [],
            'yearly_activity': yearly_activity.split('\n') if yearly_activity else []
        }
        
        return self.results['contributors']
    
    def calculate_suitability_score(self):
        """Calcula score de adequação do repositório"""
        print("Calculando score de adequação")
        
        metrics = self.results['basic_metrics']
        score = 0
        
        commits_per_year = metrics['total_commits'] / max(metrics['repository_age_days'] / 365, 1)
        score += min(commits_per_year / 100, 20) 
        
        score += min(metrics['contributor_count'] * 2, 20)  
        
        structure_changes = self.results.get('metamodel_stats', {}).get('structure_commits_count', 0)
        score += min(structure_changes / 10, 20)  
        
        breaking_changes = len([c for c in self.results['metamodel_changes'] if c['is_breaking']])
        score += min(breaking_changes * 2, 20) 
        
        if metrics['mps_files_count'] > 50:
            score += 10
        if metrics['repository_age_days'] > 365 * 2:  
            score += 10
        
        return min(score, 100)
    
    def generate_report(self):
        """Gera relatório completo"""
        print("Gerando relatório")
        
        score = self.calculate_suitability_score()
        
        report = f"""
=== RELATÓRIO DE ANÁLISE MPS ===
Repositório: {self.repo_path.name}
Data da análise: {datetime.now().strftime('%Y-%m-%d %H:%M')}

MÉTRICAS BÁSICAS:
- Total de commits: {self.results['basic_metrics']['total_commits']}
- Contribuidores: {self.results['basic_metrics']['contributor_count']}
- Arquivos .mps: {self.results['basic_metrics']['mps_files_count']}
- Idade (dias): {self.results['basic_metrics']['repository_age_days']}

EVOLUÇÃO DE METAMODELO:
- Commits estruturais: {self.results.get('metamodel_stats', {}).get('structure_commits_count', 0)}
- Mudanças breaking: {len([c for c in self.results['metamodel_changes'] if c['is_breaking']])}

SCORE DE ADEQUAÇÃO: {score:.1f}/100

STATUS: {'ADEQUADO' if score >= 70 else ' LIMITADO' if score >= 50 else ' INADEQUADO'}
"""
        
        return report
    
    def export_data(self, output_file='mps_analysis.json'):
        """Exporta dados para arquivo JSON"""
        self.results['suitability_score'] = self.calculate_suitability_score()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"Dados exportados para: {output_file}")

def main():
    """Função principal - exemplo de uso"""
    
    repositories = [
        "repositories/mbeddr.core",
        "repositories/iets3.opensource", 
        "repositories/selfadaptive-IoT-DSL"
    ]
    
    results_summary = []
    
    for repo_path in repositories:
        if not os.path.exists(repo_path):
            print(f"Repositório não encontrado: {repo_path}")
            continue
            
        print(f"\nAnalisando: {repo_path}")
        print("=" * 50)
        
        analyzer = MPSRepositoryAnalyzer(repo_path)
        
        analyzer.analyze_basic_metrics()
        analyzer.analyze_metamodel_changes()
        analyzer.analyze_contributors()
        
        report = analyzer.generate_report()
        print(report)
        
        output_file = f"analysis_{Path(repo_path).name}.json"
        analyzer.export_data(output_file)
        
        results_summary.append({
            'repository': Path(repo_path).name,
            'score': analyzer.calculate_suitability_score(),
            'output_file': output_file
        })
        print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    
    for result in sorted(results_summary, key=lambda x: x['score'], reverse=True):
        print(f"{result['repository']:30} Score: {result['score']:5.1f} ({result['output_file']})")

if __name__ == "__main__":
    main()