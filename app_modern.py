import streamlit as st
import pandas as pd
import re
from typing import Dict, List, Tuple
from collections import defaultdict
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="AWS Cost Calculator",
    page_icon="06 - Dati Símbolo Oficial.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado com paleta de cores personalizada
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1b0f5d 0%, #655ccb 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: #ffffff;
        text-align: center;
        box-shadow: 0 8px 32px rgba(27, 15, 93, 0.3);
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(27, 15, 93, 0.1);
        border-left: 4px solid #f59d01;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(27, 15, 93, 0.15);
    }
    
    .service-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #5bbed6;
        box-shadow: 0 2px 8px rgba(91, 190, 214, 0.1);
    }
    
    .upload-area {
        border: 2px dashed #f59d01;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(45deg, #ffffff 0%, #f8f9ff 100%);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #655ccb;
        background: linear-gradient(45deg, #f8f9ff 0%, #ffffff 100%);
    }
    
    .success-banner {
        background: linear-gradient(45deg, #a1dfb4 0%, #c8e6c9 100%);
        border: 1px solid #a1dfb4;
        color: #1b5e20;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(161, 223, 180, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #f59d01 0%, #ff9800 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #e68900 0%, #f57c00 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(245, 157, 1, 0.4);
    }
    
    .sidebar .stSelectbox > div > div {
        background-color: #ffffff;
        border: 1px solid #5bbed6;
    }
    
    .sidebar .stNumberInput > div > div > input {
        background-color: #ffffff;
        border: 1px solid #5bbed6;
    }
    
    h1, h2, h3 {
        color: #1b0f5d;
    }
    
    .main-header h1 {
        color: #ffffff !important;
    }
    
    .stMetric {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #655ccb;
    }
</style>
""", unsafe_allow_html=True)

def extract_instance_details(config_text: str, service: str) -> Dict:
    """Extrai detalhes das instâncias do texto de configuração"""
    details = {'quantidade': 1, 'tipo': 'N/A', 'specs': []}
    
    if "EC2" in service:
        instance_match = re.search(r'Instância do EC2 avançada \(([^)]+)\)|Advance EC2 instance \(([^)]+)\)', config_text)
        if instance_match:
            details['tipo'] = instance_match.group(1) or instance_match.group(2)
        
        qty_match = re.search(r'Número de instâncias: (\d+)|Number of instances: (\d+)', config_text)
        if qty_match:
            details['quantidade'] = int(qty_match.group(1) or qty_match.group(2))
        
        pricing_match = re.search(r'Pricing strategy \(([^)]+)\)', config_text)
        pricing_strategy = pricing_match.group(1) if pricing_match else 'N/A'
        
        os_match = re.search(r'Sistema operacional \(([^)]+)\)|Operating system \(([^)]+)\)', config_text)
        os_system = (os_match.group(1) or os_match.group(2)) if os_match else 'N/A'
        
        details['specs'] = [pricing_strategy, os_system]
    
    elif "RDS" in service or "Aurora" in service:
        instance_match = re.search(r'Tipo de instância \(([^)]+)\)|Instance type \(([^)]+)\)', config_text)
        if instance_match:
            details['tipo'] = instance_match.group(1) or instance_match.group(2)
        
        nodes_match = re.search(r'Nós \((\d+)\)|Nodes \((\d+)\)', config_text)
        if nodes_match:
            details['quantidade'] = int(nodes_match.group(1) or nodes_match.group(2))
        
        az_config = 'Single AZ'
        if 'Multi' in config_text or 'multi' in config_text:
            az_config = 'Multi AZ'
        
        purchase_option = 'Reserved Instance'
        if 'OnDemand' in config_text:
            purchase_option = 'On Demand'
        elif 'No Upfront' in config_text:
            purchase_option = 'No Upfront'
        elif 'All Upfront' in config_text:
            purchase_option = 'All Upfront'
        
        period = '1 ano'
        if '3 year' in config_text.lower() or '3-year' in config_text.lower():
            period = '3 anos'
        
        engine_type = service
        details['specs'] = [az_config, purchase_option, period, engine_type]
    
    elif "ElastiCache" in service:
        instance_types = re.findall(r'Tipo de instância \(([^)]+)\)|Instance type \(([^)]+)\)', config_text)
        nodes_counts = re.findall(r'Nós \((\d+)\)|Nodes \((\d+)\)', config_text)
        
        instance_types = [match[0] or match[1] for match in instance_types]
        nodes_counts = [int(match[0] or match[1]) for match in nodes_counts]
        
        for i, instance_type in enumerate(instance_types):
            if i < len(nodes_counts):
                nodes = nodes_counts[i]
                if nodes > 0 and 'r6gd.12xlarge' not in instance_type:
                    details['tipo'] = instance_type
                    details['quantidade'] = nodes
                    break
        
        purchase_option = 'Reserved Instance'
        if 'OnDemand' in config_text:
            purchase_option = 'On Demand'
        elif 'Heavy Utilization' in config_text:
            purchase_option = 'Heavy Utilization'
        elif 'No Upfront' in config_text:
            purchase_option = 'No Upfront'
        elif 'All Upfront' in config_text:
            purchase_option = 'All Upfront'
        
        period = '1 ano'
        if '3 year' in config_text.lower() or '3-year' in config_text.lower():
            period = '3 anos'
        
        cache_engine = 'Redis'
        if 'Valkey' in config_text:
            cache_engine = 'Valkey'
        elif 'Memcached' in config_text:
            cache_engine = 'Memcached'
        
        details['specs'] = [purchase_option, period, cache_engine]
    
    elif "AWS Fargate" in service or "Fargate" in service:
        architecture = 'x86'
        if 'ARM' in config_text:
            architecture = 'ARM'
        
        os_system = 'Linux'
        if 'Windows' in config_text:
            os_system = 'Windows'
        
        details['specs'] = [architecture, os_system]
    
    return details

def load_csv_file(file_path_or_buffer) -> pd.DataFrame:
    """Carrega o CSV lidando com a estrutura complexa do arquivo AWS"""
    if hasattr(file_path_or_buffer, 'read'):
        content = file_path_or_buffer.read().decode('utf-8-sig')
        lines = content.split('\n')
    else:
        with open(file_path_or_buffer, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    
    start_idx = -1
    for i, line in enumerate(lines):
        if 'Estimativa detalhada' in line or 'Detailed Estimate' in line:
            start_idx = i + 1
            break
    
    if start_idx == -1:
        raise ValueError("Seção 'Estimativa detalhada' ou 'Detailed Estimate' não encontrada")
    
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip() == '' or 'Confirmação' in lines[i] or 'Acknowledgement' in lines[i]:
            end_idx = i
            break
    
    data_lines = lines[start_idx:end_idx]
    
    from io import StringIO
    csv_data = '\n'.join(data_lines)
    df = pd.read_csv(StringIO(csv_data))
    
    return df

def process_csv(df: pd.DataFrame, lambda_payment_option: str = "No Upfront 12x pela AWS", fargate_payment_option: str = "No Upfront 12x pela AWS") -> Dict:
    """Processa o DataFrame e extrai informações relevantes"""
    result = {
        'client_name': '',
        'account_id': '',
        'services_by_region': defaultdict(lambda: defaultdict(list)),
        'regions': set(),
        'total_costs': {'no_upfront': 0, 'all_upfront': 0}
    }
    
    if not df.empty and 'Hierarquia de grupos' in df.columns:
        first_hierarchy = df['Hierarquia de grupos'].iloc[0]
        if ' > ' in first_hierarchy:
            client_account = first_hierarchy.split(' > ')[0].strip()
            
            if ' - ' in client_account:
                parts = client_account.split(' - ')
                if len(parts) >= 3:
                    result['client_name'] = ' - '.join(parts[:-1]).strip()
                    result['account_id'] = parts[-1].strip()
                elif len(parts) == 2:
                    result['client_name'] = parts[0].strip()
                    result['account_id'] = parts[1].strip()
            elif ' ' in client_account:
                client_parts = client_account.rsplit(' ', 1)
                result['client_name'] = client_parts[0].strip()
                result['account_id'] = client_parts[1].strip()
    
    for _, row in df.iterrows():
        region = row['Região']
        service = row['Serviço']
        upfront = float(row['Pagamento adiantado']) if pd.notna(row['Pagamento adiantado']) else 0
        monthly = float(row['Mensal']) if pd.notna(row['Mensal']) else 0
        config = row['Resumo da configuração']
        hierarchy = row['Hierarquia de grupos']
        
        result['regions'].add(region)
        
        payment_mode = 'No Upfront'
        total_cost = 0
        
        if 'All Upfront' in hierarchy or 'ALL Upfront' in hierarchy or 'All UpFront' in hierarchy:
            if "ElastiCache" in service and "cache.t2.micro" in config:
                payment_mode = 'Heavy Utilization'
            else:
                payment_mode = 'All Upfront'
            total_cost = upfront
        elif 'Heavy Utilization' in config:
            payment_mode = 'Heavy Utilization'
            total_cost = upfront
        elif 'No Upfront' in hierarchy or 'No UpFront' in hierarchy or 'No-UpFront' in hierarchy:
            payment_mode = 'No Upfront'
            total_cost = monthly
        else:
            payment_mode = 'No Upfront'
            total_cost = monthly
        
        # Aplicar descontos específicos
        if "CloudFront" in service:
            payment_mode = 'No Upfront'
            # Garantir que usa o valor mensal correto e aplica 30% de desconto
            base_cost = monthly if monthly > 0 else upfront
            total_cost = base_cost * 0.7  # 30% desconto
        elif "AWS Lambda" in service or "Lambda" in service:
            # Lambda sempre processa (mesmo On Demand)
            payment_mode = 'All Upfront' if 'All Upfront' in lambda_payment_option else 'No Upfront'
            is_sao_paulo = 'São Paulo' in region or 'América do Sul' in region
            
            if payment_mode == 'All Upfront':
                base_cost = upfront if upfront > 0 else monthly
            else:
                base_cost = monthly
            
            if is_sao_paulo:
                if payment_mode == 'All Upfront':
                    total_cost = base_cost * 0.85  # 15% desconto
                else:
                    total_cost = base_cost * 0.90  # 10% desconto
            else:
                if payment_mode == 'All Upfront':
                    total_cost = base_cost * 0.83  # 17% desconto
                else:
                    total_cost = base_cost * 0.88  # 12% desconto
        elif "AWS Fargate" in service or "Fargate" in service:
            # Fargate sempre processa (mesmo On Demand)
            payment_mode = 'All Upfront' if 'All Upfront' in fargate_payment_option else 'No Upfront'
            is_arm = 'ARM' in config
            is_sao_paulo = 'São Paulo' in region or 'América do Sul' in region
            
            # Sempre usar o valor mensal como base para Fargate
            base_cost = monthly
            
            if is_sao_paulo:
                if payment_mode == 'All Upfront':
                    if is_arm:
                        total_cost = base_cost * 0.74  # 26% desconto
                    else:
                        total_cost = base_cost * 0.78  # 22% desconto
                else:
                    if is_arm:
                        total_cost = base_cost * 0.79  # 21% desconto
                    else:
                        total_cost = base_cost * 0.85  # 15% desconto
            else:
                if payment_mode == 'All Upfront':
                    if is_arm:
                        total_cost = base_cost * 0.73  # 27% desconto
                    else:
                        total_cost = base_cost * 0.73  # 27% desconto
                else:
                    if is_arm:
                        total_cost = base_cost * 0.79  # 21% desconto
                    else:
                        total_cost = base_cost * 0.80  # 20% desconto
        elif "RDS" in service or "Aurora" in service:
            # Aplicar desconto de armazenamento para RDS No Upfront
            if payment_mode == 'No Upfront':
                base_cost = monthly
                # Verificar se tem especificação de armazenamento (20 GB)
                if "Quantidade de armazenamento (20 GB)" in config:
                    is_sao_paulo = 'São Paulo' in region or 'América do Sul' in region
                    if is_sao_paulo:
                        total_cost = base_cost - 4.38  # Desconto São Paulo
                    else:
                        total_cost = base_cost - 2.3   # Desconto outras regiões
                else:
                    total_cost = base_cost
            else:
                total_cost = upfront
        else:
            # Para outros serviços, usar a lógica padrão
            if payment_mode == 'All Upfront':
                total_cost = upfront
            else:
                total_cost = monthly
        
        # Correção especial: se upfront = 0 e monthly > 0, forçar No Upfront (exceto CloudFront, Lambda, Fargate e RDS que já têm desconto aplicado)
        if upfront == 0 and monthly > 0 and "CloudFront" not in service and "Lambda" not in service and "AWS Fargate" not in service and "Fargate" not in service and "RDS" not in service and "Aurora" not in service:
            payment_mode = 'No Upfront'
            total_cost = monthly
        
        # Pular linhas On Demand (exceto Lambda, Fargate e CloudFront)
        if ('On-demand' in hierarchy or 'On Demand' in hierarchy or 'On-Demand' in hierarchy):
            # Permitir apenas Lambda, Fargate e CloudFront em On Demand
            if ('AWS Lambda' not in service and 'Lambda' not in service and 
                'AWS Fargate' not in service and 'Fargate' not in service and 
                'CloudFront' not in service):
                continue
        
        details = extract_instance_details(config, service)
        
        service_key = None
        if "EC2" in service:
            service_key = 'EC2'
        elif "RDS" in service or "Aurora" in service:
            service_key = 'RDS'
        elif "ElastiCache" in service:
            service_key = 'ElastiCache'
        elif "CloudFront" in service:
            service_key = 'CloudFront'
        elif "AWS Lambda" in service or "Lambda" in service:
            service_key = 'Lambda'
        elif "AWS Fargate" in service or "Fargate" in service:
            service_key = 'Fargate'
        
        if service_key:
            result['services_by_region'][region][service_key].append({
                'tipo': details.get('tipo', 'N/A'),
                'quantidade': details.get('quantidade', 1),
                'specs': details.get('specs', []),
                'payment_mode': payment_mode,
                'cost': total_cost,
                'upfront': upfront,
                'service_name': service,
                'config': config
            })
            
            # Acumular custos totais
            if payment_mode == 'No Upfront':
                result['total_costs']['no_upfront'] += total_cost
            else:
                if service_key in ['Lambda', 'Fargate']:
                    result['total_costs']['all_upfront'] += total_cost * 12
                else:
                    result['total_costs']['all_upfront'] += total_cost
    
    return result

def generate_summary(data: Dict, exchange_rate: float, tax_rate: float = 13.83, lambda_payment_option: str = "No Upfront 12x pela AWS", fargate_payment_option: str = "No Upfront 12x pela AWS") -> str:
    """Gera o resumo formatado baseado nos modelos"""
    client_name = data['client_name']
    account_id = data['account_id']
    
    summary = f"Resumos dos recursos a serem reservados\n{client_name} - {account_id}\n\n"
    
    # Totais por tipo de pagamento
    total_no_upfront = 0
    total_all_upfront = 0
    
    # Processar por região
    for region in sorted(data['regions']):
        if region not in data['services_by_region']:
            continue
        
        # Mapear nome da região
        region_name = region
        if "N. da Virgínia" in region or "N. Virginia" in region or "Leste dos EUA" in region:
            region_name = "N. Virginia"
        elif "São Paulo" in region or "América do Sul" in region:
            region_name = "São Paulo"
        
        summary += f"{region_name}\n"
        
        services = data['services_by_region'][region]
        
        # Processar cada serviço
        for service_type in ['EC2', 'RDS', 'ElastiCache', 'CloudFront', 'Lambda', 'Fargate']:
            if service_type not in services or not services[service_type]:
                continue
            
            instances = services[service_type]
            
            # Agrupar por tipo de pagamento
            no_upfront_instances = [i for i in instances if i['payment_mode'] == 'No Upfront']
            all_upfront_instances = [i for i in instances if i['payment_mode'] in ['All Upfront', 'Heavy Utilization']]
            
            # Calcular totais
            no_upfront_cost = sum(i['cost'] for i in no_upfront_instances)
            all_upfront_cost = sum(i['cost'] for i in all_upfront_instances)
            
            total_no_upfront += no_upfront_cost
            # Para Lambda e Fargate All Upfront, multiplicar por 12 no total geral
            if service_type in ['Lambda', 'Fargate']:
                total_all_upfront += all_upfront_cost * 12
            else:
                total_all_upfront += all_upfront_cost
            
            # Gerar seção do serviço
            if service_type == 'EC2':
                total_instances = sum(i['quantidade'] for i in instances)
                summary += f"EC2 Instances - {total_instances:02d} instâncias - Conta AWS {account_id}\n"
                summary += "Tipos de Instancias:\n"
                
                for instance in instances:
                    pricing_strategy = instance['specs'][0] if len(instance['specs']) > 0 else 'N/A'
                    os_system = instance['specs'][1] if len(instance['specs']) > 1 else 'N/A'
                    summary += f"-{instance['quantidade']} - {instance['tipo']} ({pricing_strategy}, {os_system})\n"
                
                if no_upfront_cost > 0:
                    summary += f"Valor total No Upfront: USD {no_upfront_cost:,.2f}/mês\n"
                if all_upfront_cost > 0:
                    summary += f"Valor total All Upfront: USD {all_upfront_cost:,.2f}/ano\n"
            
            elif service_type == 'RDS':
                total_instances = sum(i['quantidade'] for i in instances)
                summary += f"RDS - {total_instances:02d} instâncias - Conta AWS {account_id}\n"
                summary += "Tipos de Instancias:\n"
                
                for instance in instances:
                    az = instance['specs'][0] if len(instance['specs']) > 0 else 'N/A'
                    purchase = instance['payment_mode']  # Usar payment_mode em vez de specs[1]
                    period = instance['specs'][2] if len(instance['specs']) > 2 else 'N/A'
                    engine = instance['specs'][3] if len(instance['specs']) > 3 else 'N/A'
                    summary += f"-{instance['quantidade']} - {instance['tipo']} ({az}, {purchase}, {period}, {engine})\n"
                
                if no_upfront_cost > 0:
                    summary += f"Valor total No Upfront: USD {no_upfront_cost:,.2f}/mês\n"
                if all_upfront_cost > 0:
                    summary += f"Valor total All Upfront: USD {all_upfront_cost:,.2f}/ano\n"
            
            elif service_type == 'ElastiCache':
                total_nodes = sum(i['quantidade'] for i in instances)
                summary += f"ElastiCache - {total_nodes:02d} nós - Conta AWS {account_id}\n"
                summary += "Tipos de Instancias:\n"
                
                for instance in instances:
                    purchase = instance['payment_mode']  # Usar payment_mode em vez de specs[0]
                    period = instance['specs'][1] if len(instance['specs']) > 1 else 'N/A'
                    cache_engine = instance['specs'][2] if len(instance['specs']) > 2 else 'N/A'
                    summary += f"-{instance['quantidade']} - {instance['tipo']} ({purchase}, {period}, {cache_engine})\n"
                
                if no_upfront_cost > 0:
                    summary += f"Valor total No Upfront: USD {no_upfront_cost:,.2f}/mês\n"
                if all_upfront_cost > 0:
                    summary += f"Valor total All Upfront: USD {all_upfront_cost:,.2f}/ano\n"
            
            elif service_type == 'CloudFront':
                summary += f"CloudFront - Conta AWS {account_id}\n"
                summary += "Período: 1 ano\n"
                summary += "Forma de pagamento: No Upfront em 12x pela AWS\n"
                summary += f"Valor total mensal: USD {no_upfront_cost:,.2f} (sem impostos)\n"
            
            elif service_type == 'Lambda':
                summary += f"Lambda - Conta AWS {account_id}\n"
                summary += f"Forma de pagamento: {lambda_payment_option}\n"
                if no_upfront_cost > 0:
                    summary += f"Valor total No Upfront: USD {no_upfront_cost:,.2f}/mês\n"
                if all_upfront_cost > 0:
                    summary += f"Valor total All Upfront: USD {all_upfront_cost * 12:,.2f}/ano\n"
            
            elif service_type == 'Fargate':
                summary += f"ECS fargate - {region_name} - Conta AWS {account_id}\n"
                summary += "Período: 1 ano\n"
                summary += f"Forma de pagamento: {fargate_payment_option}\n"
                
                # Mostrar detalhes das configurações
                for instance in instances:
                    architecture = instance['specs'][0] if len(instance['specs']) > 0 else 'x86'
                    os_system = instance['specs'][1] if len(instance['specs']) > 1 else 'Linux'
                    summary += f"Configuração: {os_system} {architecture}\n"
                
                if no_upfront_cost > 0:
                    summary += f"Valor total No Upfront: USD {no_upfront_cost:,.2f}/mês\n"
                if all_upfront_cost > 0:
                    summary += f"Valor total All Upfront: USD {all_upfront_cost * 12:,.2f}/ano\n"
            
            summary += "\n"
    
    # Resumo financeiro
    if total_all_upfront > 0:
        summary += "Resumo financeiro All Upfront:\n"
        all_upfront_taxes = total_all_upfront * (tax_rate / 100)
        all_upfront_with_taxes = total_all_upfront + all_upfront_taxes
        all_upfront_brl = all_upfront_with_taxes * exchange_rate
        all_upfront_parcela = all_upfront_brl / 6
        
        summary += f"Valor total (sem imposto): USD {total_all_upfront:,.2f}/ano\n"
        summary += f"Impostos: USD {all_upfront_taxes:,.2f}/ano\n"
        summary += f"Valor do dólar (aproximado): R$ {exchange_rate:.2f}\n"
        summary += f"Valor total em reais (com imposto): R$ {all_upfront_brl:,.2f}/ano\n"
        summary += f"Parcelamento TdSynnex(com imposto): 06x R$ {all_upfront_parcela:,.2f} via TdSynnex\n\n"
    
    if total_no_upfront > 0:
        summary += "Resumo financeiro No Upfront:\n"
        no_upfront_annual = total_no_upfront * 12
        no_upfront_taxes = no_upfront_annual * (tax_rate / 100)
        no_upfront_with_taxes = no_upfront_annual + no_upfront_taxes
        no_upfront_brl_monthly = no_upfront_with_taxes * exchange_rate / 12
        
        summary += f"Valor total (sem imposto): USD {no_upfront_annual:,.2f}/ano\n"
        summary += f"Impostos: USD {no_upfront_taxes:,.2f}/ano\n"
        summary += f"Valor do dólar (aproximado): R$ {exchange_rate:.2f}\n"
        summary += f"Valor total em reais (com imposto): 12x R$ {no_upfront_brl_monthly:,.2f} via AWS\n"
    
    return summary

def create_cost_chart(data: Dict, exchange_rate: float):
    """Cria gráfico de custos por serviço"""
    services_costs = defaultdict(float)
    
    for region_services in data['services_by_region'].values():
        for service_type, instances in region_services.items():
            total_cost = sum(i['cost'] for i in instances)
            services_costs[service_type] += total_cost
    
    if not services_costs:
        return None
    
    # Paleta de cores personalizada
    custom_colors = ['#f59d01', '#5bbed6', '#655ccb', '#a1dfb4', '#1b0f5d', '#ff9800']
    
    fig = px.pie(
        values=list(services_costs.values()),
        names=list(services_costs.keys()),
        title="Distribuição de Custos por Serviço (USD)",
        color_discrete_sequence=custom_colors
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont_size=12,
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    
    fig.update_layout(
        height=400,
        title_font_color='#1b0f5d',
        title_font_size=18,
        font=dict(color='#1b0f5d')
    )
    
    return fig

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <div class="logo-container">
            <h1 style="color: #ffffff;">AWS Cost Calculator</h1>
        </div>
        <p>Processamento inteligente de arquivos CSV da Calculadora AWS</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar com logo e configurações
    with st.sidebar:
        # Logo bem no topo
        try:
            logo = "02 - Dati Logotipo Oficial.png"
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo, width=120)
        except:
            pass
        
        st.header("⚙️ Configurações")
        
        exchange_rate = st.number_input(
            "💱 Taxa USD → BRL", 
            value=5.50, 
            min_value=1.0, 
            step=0.01,
            help="Taxa de conversão atual do dólar"
        )
        
        tax_rate = st.number_input(
            "📊 Taxa de Imposto (%)", 
            value=13.83, 
            min_value=0.0, 
            max_value=100.0,
            step=0.01
        )
        
        st.subheader("💳 Formas de Pagamento")
        
        lambda_payment_option = st.selectbox(
            "🔧 Lambda",
            ["No Upfront 12x pela AWS", "All Upfront 06x pela TdSynnex"]
        )
        
        fargate_payment_option = st.selectbox(
            "🐳 ECS Fargate",
            ["No Upfront 12x pela AWS", "All Upfront 06x pela TdSynnex"]
        )
        
        st.markdown("---")
        
        # Tema claro/escuro
        dark_mode = st.toggle("🌙 Modo Escuro", value=False)
        
        if dark_mode:
            st.markdown("""
            <style>
                .stApp {
                    background-color: #1a1a1a !important;
                    color: #ffffff !important;
                }
                .main-header {
                    background: linear-gradient(135deg, #0d0825 0%, #2d1b69 100%) !important;
                    color: #ffffff !important;
                }
                .metric-card {
                    background: #2d2d2d !important;
                    color: #ffffff !important;
                }
                .service-card {
                    background: #2d2d2d !important;
                    color: #ffffff !important;
                    border: 1px solid #444444 !important;
                }
                .upload-area {
                    background: #2d2d2d !important;
                    border-color: #f59d01 !important;
                    color: #ffffff !important;
                }
                .stSidebar {
                    background-color: #262626 !important;
                }
                .stSidebar .stMarkdown {
                    color: #ffffff !important;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #ffffff !important;
                }
                .stMetric {
                    background: #2d2d2d !important;
                    color: #ffffff !important;
                }
                .stDataFrame {
                    background: #2d2d2d !important;
                }
                .stTextArea textarea {
                    background-color: #2d2d2d !important;
                    color: #ffffff !important;
                }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
                .stApp {
                    background-color: #ffffff !important;
                    color: #1b0f5d !important;
                }
                .main-header {
                    background: linear-gradient(135deg, #1b0f5d 0%, #655ccb 100%) !important;
                    color: #ffffff !important;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #1b0f5d !important;
                }
            </style>
            """, unsafe_allow_html=True)
    
    # Upload de arquivo
    st.header("📁 Upload do Arquivo")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV da Calculadora AWS",
        type="csv",
        help="Arquivo deve ser exportado da Calculadora de Preços da AWS"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("🔄 Processando arquivo..."):
                # Carregar e processar dados
                df = load_csv_file(uploaded_file)
                
                # Verificar colunas
                required_columns_pt = ['Hierarquia de grupos', 'Região', 'Serviço', 'Pagamento adiantado', 'Mensal', 'Resumo da configuração']
                required_columns_en = ['Group hierarchy', 'Region', 'Service', 'Upfront', 'Monthly', 'Configuration summary']
                
                is_portuguese = all(col in df.columns for col in required_columns_pt)
                is_english = all(col in df.columns for col in required_columns_en)
                
                if not is_portuguese and not is_english:
                    st.error("❌ Formato de arquivo inválido. Verifique se o CSV foi exportado corretamente da Calculadora AWS.")
                    return
                
                # Normalizar colunas
                if is_english:
                    column_mapping = {
                        'Group hierarchy': 'Hierarquia de grupos',
                        'Region': 'Região',
                        'Service': 'Serviço',
                        'Upfront': 'Pagamento adiantado',
                        'Monthly': 'Mensal',
                        'Configuration summary': 'Resumo da configuração'
                    }
                    df = df.rename(columns=column_mapping)
                
                # Processar dados
                data = process_csv(df, lambda_payment_option, fargate_payment_option)
                
                if not data['account_id']:
                    st.warning("⚠️ Não foi possível extrair o ID da conta AWS")
            
            # Exibir sucesso
            st.markdown("""
            <div class="success-banner">
                ✅ <strong>Arquivo processado com sucesso!</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "🏢 Cliente", 
                    data['client_name'] or "N/A",
                    help="Nome do cliente extraído do arquivo"
                )
            
            with col2:
                st.metric(
                    "🔢 Conta AWS", 
                    data['account_id'] or "N/A",
                    help="ID da conta AWS"
                )
            
            with col3:
                st.metric(
                    "🌍 Regiões", 
                    len(data['regions']),
                    help="Número de regiões AWS utilizadas"
                )
            
            with col4:
                total_services = sum(len(instances) for region_services in data['services_by_region'].values() for instances in region_services.values())
                st.metric(
                    "⚙️ Serviços", 
                    total_services,
                    help="Total de serviços configurados"
                )
            
            # Gráfico de custos
            cost_chart = create_cost_chart(data, exchange_rate)
            if cost_chart:
                st.plotly_chart(cost_chart, use_container_width=True)
            
            # Resumo financeiro
            st.header("💰 Resumo Financeiro")
            
            # Verificar quais tipos de pagamento existem
            has_no_upfront = data['total_costs']['no_upfront'] > 0
            has_all_upfront = data['total_costs']['all_upfront'] > 0
            
            if has_no_upfront and has_all_upfront:
                # Ambos os tipos - usar 2 colunas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📅 No Upfront")
                    monthly_usd = data['total_costs']['no_upfront']
                    annual_usd = monthly_usd * 12
                    annual_brl = annual_usd * exchange_rate * 1.1383
                    monthly_brl = annual_brl / 12
                    
                    st.metric("Mensal (USD)", f"${monthly_usd:,.2f}")
                    st.metric("Anual (USD)", f"${annual_usd:,.2f}")
                    st.metric("Mensal (BRL)", f"R$ {monthly_brl:,.2f}")
                
                with col2:
                    st.subheader("💳 All Upfront")
                    annual_usd = data['total_costs']['all_upfront']
                    annual_brl = annual_usd * exchange_rate * 1.1383
                    installment_brl = annual_brl / 6
                    
                    st.metric("Anual (USD)", f"${annual_usd:,.2f}")
                    st.metric("Anual (BRL)", f"R$ {annual_brl:,.2f}")
                    st.metric("6x (BRL)", f"R$ {installment_brl:,.2f}")
            
            elif has_no_upfront:
                # Apenas No Upfront - alinhado à esquerda
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader("📅 No Upfront")
                    monthly_usd = data['total_costs']['no_upfront']
                    annual_usd = monthly_usd * 12
                    annual_brl = annual_usd * exchange_rate * 1.1383
                    monthly_brl = annual_brl / 12
                    
                    st.metric("Mensal (USD)", f"${monthly_usd:,.2f}")
                    st.metric("Anual (USD)", f"${annual_usd:,.2f}")
                    st.metric("Mensal (BRL)", f"R$ {monthly_brl:,.2f}")
            
            elif has_all_upfront:
                # Apenas All Upfront - alinhado à esquerda
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader("💳 All Upfront")
                    annual_usd = data['total_costs']['all_upfront']
                    annual_brl = annual_usd * exchange_rate * 1.1383
                    installment_brl = annual_brl / 6
                    
                    st.metric("Anual (USD)", f"${annual_usd:,.2f}")
                    st.metric("Anual (BRL)", f"R$ {annual_brl:,.2f}")
                    st.metric("6x (BRL)", f"R$ {installment_brl:,.2f}")
            
            # Resumo detalhado
            st.header("📋 Resumo Detalhado")
            
            summary = generate_summary(data, exchange_rate, tax_rate, lambda_payment_option, fargate_payment_option)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.text_area(
                    "Resumo Completo",
                    value=summary,
                    height=500,
                    help="Resumo formatado pronto para uso"
                )
            
            with col2:
                st.download_button(
                    label="📥 Download",
                    data=summary,
                    file_name=f"resumo_aws_{data['client_name']}_{data['account_id']}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    type="primary"
                )
                
                st.button(
                    "📋 Copiar",
                    help="Copiar resumo para área de transferência",
                    use_container_width=True
                )
            
            # Detalhes por região (expansível)
            with st.expander("🌍 Detalhes por Região"):
                for region in sorted(data['regions']):
                    if region in data['services_by_region']:
                        st.subheader(f"📍 {region}")
                        
                        services = data['services_by_region'][region]
                        
                        for service_type, instances in services.items():
                            if instances:
                                st.write(f"**{service_type}**: {len(instances)} instância(s)")
                                
                                service_df = pd.DataFrame([
                                    {
                                        'Tipo': inst['tipo'],
                                        'Quantidade': inst['quantidade'],
                                        'Pagamento': inst['payment_mode'],
                                        'Custo (USD)': f"${inst['cost']:.2f}"
                                    }
                                    for inst in instances
                                ])
                                
                                st.dataframe(service_df, use_container_width=True)
            
            # Debug (opcional)
            with st.expander("🔍 Dados Brutos (Debug)"):
                st.json(data)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
            st.info("💡 Verifique se o arquivo foi exportado corretamente da Calculadora AWS")

if __name__ == "__main__":
    main()