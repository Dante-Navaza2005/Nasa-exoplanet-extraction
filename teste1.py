import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any

class NASADataFetcher:
    """Classe para buscar dados de asteroides, APOD e fotos do Mars Rover da NASA."""
    
    def __init__(self, chave_api: str = 'DEMO_KEY'):
        self.chave_api = chave_api

    def buscar_dados_asteroides(self, data_inicio: str, data_fim: str) -> List[Dict[str, Any]]:
        """Busca dados de asteroides da API NeoWs da NASA."""
        url = f'https://api.nasa.gov/neo/rest/v1/feed?start_date={data_inicio}&end_date={data_fim}&api_key={self.chave_api}'
        resposta = requests.get(url)
        if resposta.status_code == 200:
            dados = resposta.json()
            lista_asteroides = [
                {
                    'Nome': ast['name'], 'ID': ast['id'], 'Data Aproximação': data,
                    'Diâmetro Mínimo (km)': ast['estimated_diameter']['kilometers']['estimated_diameter_min'],
                    'Diâmetro Máximo (km)': ast['estimated_diameter']['kilometers']['estimated_diameter_max'],
                    'Velocidade Relativa (km/s)': ast['close_approach_data'][0]['relative_velocity']['kilometers_per_second'],
                    'Distância Passagem (km)': ast['close_approach_data'][0]['miss_distance']['kilometers'],
                    'Perigoso': ast['is_potentially_hazardous_asteroid'],
                    'Data Observação': ast.get('orbital_data', {}).get('first_observation_date', 'N/A')
                } for data, asteroides in dados['near_earth_objects'].items() for ast in asteroides
            ]
            return lista_asteroides
        print(f"Erro: {resposta.status_code}")
        return []

    def buscar_apod(self, data_inicio: str, data_fim: str) -> List[Dict[str, Any]]:
        """Busca o APOD da NASA para um intervalo de datas."""
        url = 'https://api.nasa.gov/planetary/apod'
        params = {'start_date': data_inicio, 'end_date': data_fim, 'api_key': self.chave_api}
        resposta = requests.get(url, params=params)
        if resposta.status_code == 200:
            return resposta.json()
        print(f"Erro: {resposta.status_code}")
        return []

    def contar_fotos_mars_rover(self, ano: int, mes: str, dia: str) -> int:
        """Conta o número de fotos tiradas pelo Rover Curiosity em uma data específica."""
        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?earth_date={ano}-{mes}-{dia}&api_key={self.chave_api}"
        resposta = requests.get(url)
        if resposta.status_code == 200:
            dados = resposta.json()
            fotos = dados.get('photos', [])
            return len(fotos)
        print(f"Erro: {resposta.status_code}")
        return 0

class DataAnalyzer:
    """Classe para analisar e visualizar dados de asteroides, APOD e fotos do Mars Rover."""
    
    def __init__(self, coletor: NASADataFetcher, dados_asteroides_2005: pd.DataFrame, dados_asteroides_2024: pd.DataFrame, apod_data: List[List[Dict[str, Any]]]):
        self.coletor = coletor
        self.dados_asteroides = pd.concat([dados_asteroides_2005.assign(Ano=2005), dados_asteroides_2024.assign(Ano=2024)])
        self.apod_data = apod_data

    def exibir_apod_detalhes(self) -> None:
        """Exibe os detalhes das entradas APOD, incluindo título, data e link."""
        intervalos = ['2024-09-01 a 2024-09-07', '2005-09-01 a 2005-09-07']
        for i, apod in enumerate(self.apod_data):
            print(f"APOD de {intervalos[i]}:")
            for item in apod:
                print(f"Título: {item['title']}")
                print(f"Data: {item['date']}")
                print(f"URL: {item['url']}")
                print(f"Explicação: {item['explanation']}\n")

    def plotar_dados_asteroides(self) -> None:
        """Plota o número de asteroides e asteroides perigosos."""
        plt.figure(figsize=(12, 5))

        # Número de asteroides
        plt.subplot(1, 2, 1)
        contagem_asteroides = self.dados_asteroides.groupby('Ano')['ID'].count().reset_index()
        sns.barplot(x='Ano', y='ID', data=contagem_asteroides)
        plt.title('Número de Asteroides Detectados')

        # Asteroides perigosos
        plt.subplot(1, 2, 2)
        perigosos = self.dados_asteroides.groupby(['Ano', 'Perigoso'])['ID'].count().unstack().reset_index()
        perigosos.plot(kind='bar', stacked=True, x='Ano', ax=plt.gca())
        plt.title('Asteroides Potencialmente Perigosos')
        plt.show()

    def plotar_apod(self) -> None:
        """Plota o número de entradas do APOD por intervalo de datas."""
        intervalos = ['2024-09-01 a 2024-09-07', '2005-09-01 a 2005-09-07']
        contagem_apod = [len(apod) for apod in self.apod_data]
        plt.bar(intervalos, contagem_apod, color=['blue', 'orange'])
        plt.xlabel('Intervalos de Data')
        plt.ylabel('Número de Entradas APOD')
        plt.title('Comparação de Entradas APOD')
        plt.show()

    def plotar_fotos_mars_rover(self, dia: str, mes: str) -> None:
        """Plota o número de fotos tiradas pelo Rover Curiosity em datas específicas."""
        contagem_fotos = [self.coletor.contar_fotos_mars_rover(ano, mes, dia) for ano in [2015, 2023]]
        anos = ['2015', '2023']
        plt.bar(anos, contagem_fotos, color=['blue', 'orange'])
        plt.xlabel('Ano')
        plt.ylabel('Número de Fotos')
        plt.title(f'Fotos tiradas pelo Curiosity em {dia}/{mes} em 2015 e 2023')
        plt.show()

def main() -> None:
    """Função principal para executar a busca e análise de dados da NASA."""
    CHAVE_API = 'DEMO_KEY'
    coletor = NASADataFetcher(chave_api=CHAVE_API)
    
    # Definir intervalos de datas
    intervalos_datas = [('2024-09-01', '2024-09-07'), ('2005-09-01', '2005-09-07')]

    # Buscar dados de asteroides
    dados_asteroides_2024 = pd.DataFrame(coletor.buscar_dados_asteroides(*intervalos_datas[0]))
    dados_asteroides_2005 = pd.DataFrame(coletor.buscar_dados_asteroides(*intervalos_datas[1]))
    
    # Buscar dados APOD
    apod_data = [coletor.buscar_apod(*intervalo) for intervalo in intervalos_datas]
    
    # Analisar e visualizar os dados
    analisador = DataAnalyzer(coletor, dados_asteroides_2005, dados_asteroides_2024, apod_data)
    analisador.exibir_apod_detalhes()  # Exibe os detalhes do APOD
    analisador.plotar_dados_asteroides()
    analisador.plotar_apod()
    
    # Plotar fotos do Mars Rover
    analisador.plotar_fotos_mars_rover("03", "06")

if __name__ == "__main__":
    main()

