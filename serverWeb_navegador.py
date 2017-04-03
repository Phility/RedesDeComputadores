#Redes de Computadores
#Unviversidade Federal do Rio Grande do Norte
#Departamento de Engenharia de Computação e Automação
#Alunos: Carlos Gabriel Gomes de Melo Silva
#        Philipy Augusto Silveira de Brito

#Programa que simula um servidor web

import socket
import os

# Definicao do host e da porta do servidor
HOST = '' # opcional
PORT = 8080

# Cria o socket com IPv4 (AF_INET) usando TCP (SOCK_STREAM)
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Mantem o socket ativo mesmo apos a conexao ser encerrada (faz o reuso do endereco do servidor)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Vincula o socket com a porta (faz o "bind" do servidor com a porta)
listen_socket.bind((HOST, PORT))

# "Escuta" pedidos na porta do socket do servidor
listen_socket.listen(1)

# Imprime que o servidor esta pronto para receber conexoes
print 'Serving HTTP on port %s ...' % PORT

def startServer():
    while True:
        # Aguarda por novas conexoes
        client_connection, client_address = listen_socket.accept()

        #Declaracao de variaveis
        response_control =  False
        http_response = ""
        bad_request = 'HTTP/1.0 400 Bad Request \r\n\r\n <html><head></head><body><h1>400 Bad Resquest</h1></body></html>\r\n'
        not_found = 'HTTP/1.0 404 Not Found\r\n\r\n <html><head></head><body><h1>404 Not Found</h1></body></html>\r\n'
        no_content = 'HTTP/1.0 204 No Content\r\n\r\n <html><head></head><body><h1>204 No Content</h1></body></html>\r\n'
        get = 'GET /'
        http = 'HTTP'
        httpNavegador = 'HTTP/'
        versao11 = '1.1'
        versao10 = '1.0'
        delete = 'DELETE /'
        path = ''
        
        while response_control == False:
            responde_control = True
            path = '' #Inicia novamente a variavel path em caso de erro BAD REQUEST
            # O metodo .recv recebe os dados enviados por um cliente atraves do socket
            request = client_connection.recv(1024)
            # Imprime na tela o que o cliente enviou ao servidor
            #Separamos a requisicao para fins de comparacao do comando GET HTTP
            request_nav = request.split('\r\n') #Aqui trata os caracteres '\r\n' a fim de elimina-los do comando GET HTTP, tambem adapta o comando feito pelo navegador
            request_split = request_nav[0].split(' ') #Aqui separamos o comando GET HTTP em partes utilizando o caractere 'espaco'
            #Pegamos o tamanho do .split, pois caso seja escrito tudo junto, retornara BAD REQUEST
            request_size = len(request_split)
            #Comparamos o tamanho do .split
            #Se o comando digitado nao possuir 4 ou 3 na divisao nem fazemos o resto do trabalho, vai ser retornado BAD REQUEST
            if request_size == 4 or request_size == 3:
                #Salvamos nas variaveis as partes da requisicao
                if (request_size == 4):
                    request_command = request_split[0]
                    request_path = request_split[1]
                    request_http = request_split[2]
                    request_versao = request_split[3]
                    if (request_path[0] == '/'):
                        for i in range (1, len(request_path)):
                            path += request_path[i]
                        request_command += ' /'
                        #Fazemos as comparacoes para saber se o comando GET foi digitado corretamente, caso nao retorna BAD REQUEST
                        if ((get == request_command) or (delete == request_command)) and ((http == request_http) or (httpNavegador == request_http)) and ((versao10 == request_versao) or (versao11 == request_versao)):
                            response_control = True
                        else:
                            client_connection.send(bad_request)
                            response_control = False
                    else:
                        client_connection.send(bad_request)
                        response_control = False
                elif (request_size == 3):
                    request_command = request_split[0]
                    request_path = request_split[1]
                    request_http = request_split[2]
                    #Se faz necessario verificar se o caminho comeca com '/' para que possamos adicionar ao request_command, pois eh retirada quando fazemos o .split
                    if (request_path[0] == '/'):
                        for i in range (1, len(request_path)):
                            path += request_path[i]
                        request_command += ' /'
                        #Na requisicao feita pelo navegador utiliza o HTTP/(versao) tratamos esse caso na comparacao do if, para isso concatenamos HTTP/ com a versao
                        http_versao10 = httpNavegador+versao10
                        http_versao11 = httpNavegador+versao11
                        #Fazemos as comparacoes para saber se o comando GET foi digitado corretamente, caso nao retorna BAD REQUEST
                        if ((get == request_command) or (delete == request_command)) and ((http_versao10 == request_http) or (http_versao11 == request_http)):
                            response_control = True
                        else:
                            client_connection.send(bad_request)
                            response_control = False
                    else:
                        client_connection.send(bad_request)
                        response_control = False
                else:
                    client_connection.send(bad_request)
                    response_control = False
            else:
                client_connection.send(bad_request)
                response_control = False
        #Caso o comando tenha sido digitado corretamente, iremos tratar o caminho passado pelo usuario       
        if (response_control == True):
            #Usamos a funcao split para pegar a ultima parte do caminho, no caso o arquivo que sera aberto, para assim fazer a verificao se foi digitado com a extensao do arquivo ou nao
            path_split = path.split('/')
            path_size = len(path_split)
            #Caso nao tenha a extensao, adicionamos
            if (not ('.html' in path_split[path_size-1])):
                path += '.html'
            
            ## INICIO COMANDO GET ##
            if(get == request_command):
                #Tentamo abrir o arquivo passado pelo usuario
                try:
                    #Abrimos o arquivo em modo leitura
                    print path
                    f = open(path, "r")
                    #A funcao read eh um ponteiro, fazendo f.read(3), "lemos" os 3 primeiros caracteres sem salvar. Isso eh necessario devido a caracteres estranhos que estavam aparecendo no arquivo e impedindo o retorno ao cliente
                    #f.read(3) #Em alguns testes apareciam caracteres estranhos nas 3 primeiras posicoes do arquivo HTML com isso a gente tirava os caracteres
                    #Salvamos o restante do arquivo solicitado em uma variavel
                    http_response = f.read()
                    #Fechamos o arquivo
                    f.close()
                    # Servidor retorna o que foi solicitado pelo cliente
                    client_connection.send(http_response)
                except:
                    #Caso o arquivo nao exista, retornamos not found
                    client_connection.send(not_found)
            ## FIM COMANDO GET ##

            ## INICIO COMANDO DELETE ##
            elif(delete == request_command):
                try:
                    #Remove o arquivo solicitado
                    os.remove(path)
                    #Retorna para o cliente No Content
                    client_connection.send(no_content)
                except:
                    #Casoo arquivo nao exista, retornamos not found
                    client_connection.send(not_found)
            ##FIM COMANDO DELETE
                
        # Encerra a conexao
        client_connection.close()
        
startServer()
