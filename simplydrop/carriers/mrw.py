#!venv/bin/python
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# --------------------mrw.py--------------------------------
# Fichero que obtiene datos del pedido que se le ha pasado por Webhook.
# Comprueba datos y se los pasa a mrw en formato JSON para crear orden
# ---------------------------------------------------------------------

import requests
import unidecode

import simplydrop.bbdd
import simplydrop.notifier.send_email


# POST /MRWEnvio.asmx HTTP/1.1
# Host - test: http://sagec-test.mrw.es/MRWEnvio.asmx?WSDL
# Host - test: http://sagec.mrw.es/MRWEnvio.asmx?WSDL
# Content-Type: application/soap+xml; charset=utf-8 Content-Length: length


def create_mrw_order(pickupAccount, shop_url, webhook_data):
    # variables del user
    user = pickupAccount["user"]
    password = pickupAccount["password"]
    cod_fram = pickupAccount["codFran"]
    cod_abon = pickupAccount["codAbon"]
    cod_depa = pickupAccount["codDepa"]

    email_shop_contact = simplydrop.bbdd.get_shop_contact(shop_url)

    # variables del comprador
    customer_email = webhook_data["email"]
    customer_country = webhook_data["shipping_address"]["country"]
    customer_city = webhook_data["shipping_address"]["city"]
    customer_province = webhook_data["shipping_address"]["province"]
    customer_zip = webhook_data["shipping_address"]["zip"]
    customer_name = webhook_data["shipping_address"]["first_name"]
    customer_phone = webhook_data["shipping_address"]["first_name"]
    customer_address1 = webhook_data["shipping_address"]["address1"]
    customer_address2 = webhook_data["shipping_address"]["address2"]
    customer_company = webhook_data["shipping_address"]["company"]
    customer_id = webhook_data["customer"]["id"]
    amount_no_taxes = webhook_data["total_tax_set"]["shop_money"]["amount"]
    amount_no_shipping = \
        webhook_data["total_shipping_price_set"]["shop_money"]["amount"]
    total_amount = webhook_data["total_price_set"]["shop_money"]["amount"]
    shipping_type = webhook_data["shipping_lines"][0]["title"]
    currency = webhook_data["currency"]

    # variables del pedido
    shopify_order_number = webhook_data["order_number"]

    if customer_country == "Spain":

        url = "http://sagec-test.mrw.es/MRWEnvio.asmx?WSDL"
        # headers = {'content-type': 'application/soap+xml'}
        headers = {'content-type': 'text/xml'}
        body = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:mrw="http://www.mrw.es/">
                        <soap:Header>
                            <mrw:AuthInfo>
                                <mrw:CodigoFranquicia>""" + cod_fram + """</mrw:CodigoFranquicia>
                                <mrw:CodigoAbonado>""" + cod_abon + """</mrw:CodigoAbonado>
                                <mrw:CodigoDepartamento>""" + cod_depa + """</mrw:CodigoDepartamento>
                                <mrw:UserName>""" + user + """</mrw:UserName>
                                <mrw:Password>""" + password + """</mrw:Password>
                            </mrw:AuthInfo>
                        </soap:Header>
                        <soap:Body>
                            <mrw:TransmEnvio>
                                <mrw:request>
                                    <mrw:DatosEntrega>
                                       
                                        <mrw:Direccion>
                                            <mrw:CodigoDireccion>String</mrw:CodigoDireccion>
                                            <mrw:CodigoTipoVia>String</mrw:CodigoTipoVia>
                                            <mrw:Via>String</mrw:Via>
                                            <mrw:Numero>String</mrw:Numero>
                                            <mrw:Resto>""" + customer_address1 + """</mrw:Resto>
                                            <mrw:CodigoPostal>""" + customer_address2 + """</mrw:CodigoPostal>
                                            <mrw:Poblacion>""" + customer_address2 + """</mrw:Poblacion>
                                            <mrw:Estado>String</mrw:Estado>
                                            <mrw:CodigoPais>""" + customer_address2 + """</mrw:CodigoPais>
                                            <mrw:TipoPuntoEntrega>String</mrw:TipoPuntoEntrega>
                                            <mrw:CodigoPuntoEntrega>String</mrw:CodigoPuntoEntrega>
                                            <mrw:CodigoFranquiciaAsociadaPuntoEntrega>String
                                            </mrw:CodigoFranquiciaAsociadaPuntoEntrega>
                                            <mrw:Agencia>String</mrw:Agencia>
                                        </mrw:Direccion>
                                        
                                        <mrw:Nif>String</mrw:Nif>
                                        <mrw:Nombre>""" + customer_address2 + """</mrw:Nombre>
                                        <mrw:Telefono>""" + customer_address2 + """</mrw:Telefono>
                                        <mrw:Contacto>""" + customer_address2 + """</mrw:Contacto>
                                        <mrw:ALaAtencionDe>""" + customer_address2 + """</mrw:ALaAtencionDe>
                                        <mrw:Horario>
                                            <mrw:Rangos>
                                            
                                                <!--Zero or more repetitions:-->
                                                <mrw:HorarioRangoRequest>
                                                    <mrw:Desde>String</mrw:Desde>
                                                    <mrw:Hasta>String</mrw:Hasta>
                                                </mrw:HorarioRangoRequest>
                                            </mrw:Rangos>
                                        </mrw:Horario>
                                        <mrw:Observaciones>String</mrw:Observaciones>
                                    </mrw:DatosEntrega>
                                    
                                    
                                    
                                    <mrw:DatosServicio>
                                        <mrw:Fecha>""" + customer_address2 + """</mrw:Fecha>
                                        <mrw:NumeroAlbaran>String</mrw:NumeroAlbaran>
                                        <mrw:Referencia>String</mrw:Referencia>
                                        <mrw:EnFranquicia>A</mrw:EnFranquicia>????????????????????????????
                                        <mrw:CodigoServicio>0800</mrw:CodigoServicio>??????????????
                                        <mrw:DescripcionServicio>String</mrw:DescripcionServicio>
                                        <mrw:Frecuencia>String</mrw:Frecuencia>
                                        <mrw:CodigoPromocion>String</mrw:CodigoPromocion>
                                        <mrw:NumeroSobre>String</mrw:NumeroSobre>
                                        <mrw:Bultos>
                                        
                                            <!--Zero or more repetitions:-->
                                            <mrw:BultoRequest>
                                                <mrw:Alto>String</mrw:Alto>
                                                <mrw:Largo>String</mrw:Largo>
                                                <mrw:Ancho>String</mrw:Ancho>
                                                <mrw:Dimension>String</mrw:Dimension>
                                                <mrw:Referencia>String</mrw:Referencia>
                                                <mrw:Peso>String</mrw:Peso>
                                            </mrw:BultoRequest>
                                        </mrw:Bultos>
                                        
                                        <mrw:NumeroBultos>""" + customer_address2 + """</mrw:NumeroBultos>
                                        <mrw:Peso>""" + customer_address2 + """</mrw:Peso>
                                        <mrw:NumeroPuentes>String</mrw:NumeroPuentes>
                                        <mrw:EntregaSabado>String</mrw:EntregaSabado>
                                        <mrw:Entrega830>String</mrw:Entrega830>
                                        <mrw:EntregaPartirDe>String</mrw:EntregaPartirDe>
                                        <mrw:Gestion>String</mrw:Gestion>
                                        <mrw:Retorno>String</mrw:Retorno>
                                        <mrw:ConfirmacionInmediata>String</mrw:ConfirmacionInmediata>
                                        <mrw:Reembolso>String</mrw:Reembolso>
                                        <mrw:ImporteReembolso>String</mrw:ImporteReembolso>
                                        <mrw:TipoMercancia>String</mrw:TipoMercancia>
                                        <mrw:ValorDeclarado>String</mrw:ValorDeclarado>
                                        <mrw:ServicioEspecial>String</mrw:ServicioEspecial>
                                        <mrw:CodigoMoneda>String</mrw:CodigoMoneda>
                                        <mrw:ValorEstadistico>String</mrw:ValorEstadistico>
                                        <mrw:ValorEstadisticoEuros>String</mrw:ValorEstadisticoEuros>
                                        <mrw:Notificaciones>
                                        
                                            <!--Zero or more repetitions:-->
                                            <mrw:NotificacionRequest>
                                                <mrw:CanalNotificacion>String</mrw:CanalNotificacion>
                                                <mrw:TipoNotificacion>String</mrw:TipoNotificacion>
                                                <mrw:MailSMS>String</mrw:MailSMS>
                                            </mrw:NotificacionRequest>
                                
                                        </mrw:Notificaciones>
                                        <mrw:SeguroOpcional>
                                            <mrw:CodigoNaturaleza>String</mrw:CodigoNaturaleza>
                                            <mrw:ValorAsegurado>String</mrw:ValorAsegurado>
                                        </mrw:SeguroOpcional>
                                        <mrw:TramoHorario>String</mrw:TramoHorario>
                                        <mrw:PortesDebidos>String</mrw:PortesDebidos>
                                    </mrw:DatosServicio>
                                </mrw:request>
                            </mrw:TransmEnvio>
                        </soap:Body>
                    </soap:Envelope>"""

        unaccented_body = unidecode.unidecode(body)

        response = requests.post(url, data=unaccented_body, headers=headers)
        print(response.content)

        # Cabiar a false si la respuesta no es OK
        return True

    else:
        simplydrop.notifier.send_email.error_mrw_email(email_shop_contact,
                                                       shopify_order_number)
        return False
