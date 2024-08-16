from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, EKS, Lambda
from diagrams.aws.database import RDS
from diagrams.aws.integration import SQS
from diagrams.aws.storage import S3
from diagrams.aws.network import ELB
from diagrams.onprem.network import Internet  # Para representar a API de pagamento externa

with Diagram("Café App Architecture - Add Merge", show=False):
    # Nível 1: Infraestrutura
    k8s_source = EKS("k8s cluster")

    # Nível 2: Load Balancer
    with Cluster("Load Balancer"):
        elb = ELB("load_balancer")

    # Nível 2: Order Processing
    with Cluster("Order Processing"):
        order_service = ECS("order_service")
        payment_service = ECS("payment_service")
        delivery_service = ECS("delivery_service")
        
        # Adicionando Lambdas para processamento de pedidos
        order_processor = Lambda("order_processor")
        payment_processor = Lambda("payment_processor")
        delivery_processor = Lambda("delivery_processor")

    # Nível 2: Product Management
    with Cluster("Product Management"):
        product_service = ECS("product_service")
        
        # Adicionando Lambda para gerenciamento de produtos
        product_manager = Lambda("product_manager")

    # Fila de eventos
    order_queue = SQS("order_queue")

    # Nível 2: Analytics
    with Cluster("Analytics"):
        analytics_proc1 = Lambda("analytics_proc1")
        analytics_proc2 = Lambda("analytics_proc2")

    # Nível 3: Storage
    user_data = S3("user_data")        # Usando S3 para dados de usuários
    order_data = RDS("order_data")
    product_data = S3("product_data")  # Armazenamento de dados e imagens de produtos
    product_db = RDS("product_db")      # Banco de dados relacional para informações dos produtos

    # Nível 4: API de Pagamento
    payment_api = Internet("Payment API")

    # Fluxo de Dados
    k8s_source >> elb
    elb >> order_service
    elb >> product_service
    
    # Adicionando processamento Lambda para pedidos
    order_service >> order_processor
    payment_service >> payment_processor
    delivery_service >> delivery_processor
    
    order_processor >> order_queue
    payment_processor >> order_queue
    delivery_processor >> order_queue
    
    order_queue >> analytics_proc1
    order_queue >> analytics_proc2
    
    order_service >> order_data
    payment_service >> order_data
    delivery_service >> order_data
    
    analytics_proc1 >> user_data
    analytics_proc2 >> user_data
    analytics_proc1 >> product_data
    analytics_proc2 >> product_data
    
    # Cadastro e gerenciamento de produtos
    product_service >> product_manager
    product_manager >> product_db
    product_manager >> product_data

    # Integração com a API de Pagamento
    payment_processor >> payment_api
