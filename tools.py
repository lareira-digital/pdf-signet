

from pyhanko import stamp
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers, fields
from pyhanko.pdf_utils import text, images, layout
from pyhanko.pdf_utils.font import opentype
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import NameOID


def extract_pkcs12_info(pfx_file_path, password):

    # Load the PKCS#12 data
    with open(pfx_file_path, "rb") as pfx_file:
        pfx_data = pfx_file.read()

    # Unpack the PKCS#12 data
    private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
        pfx_data, password
    )
    
    issuer_info = "Autofirmado" if certificate.issuer == certificate.subject else certificate.issuer
    
    cert_info = {
        "subject": certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value,
        "issuer": issuer_info,
        "serial_number": certificate.serial_number,
        "signature_hash_algorithm": (
            certificate.signature_hash_algorithm.name
            if hasattr(certificate, "signature_hash_algorithm")
            else None
        ),
        "private_key": pfx_file_path,
        "certificate": certificate,
        "additional_certs": additional_certs,
        "url": "",
        "organization": certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value,
        "location": certificate.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value,
        "email": certificate.subject.get_attributes_for_oid(NameOID.EMAIL_ADDRESS)[0].value,
    }

    return cert_info


def sign_pdf(signature_data):
    with open(signature_data.get("invoice_path", ""), "rb") as in_file:
        cert_info = extract_pkcs12_info(
            signature_data.get("certificate", ""),
            signature_data.get("certificate_password", "").encode("utf-8"),
        )

        signer = signers.SimpleSigner.load_pkcs12(
            signature_data.get("certificate", ""),
            passphrase=signature_data.get("certificate_password", "").encode("utf-8"),
        )

        writer = IncrementalPdfFileWriter(in_file)

        fields.append_signature_field(
            writer,
            sig_field_spec=fields.SigFieldSpec(
                "Signature", box=(50, 50, 200, 120), on_page=1
            ),
        )
        
        signature_meta = signers.PdfSignatureMetadata(
            field_name="Signature", reason="Razon", location="Aqui"
        )

        stamp_text = signature_data.get("signature_text", "")
        # TODO: Lets hope that this doesnt break. We need to find a better solution
        new_stamp_text = (
            stamp_text.replace("\r", "").replace("\\r", "").replace("\\n", "\n")
        )

        pdf_signer = signers.PdfSigner(
            signature_meta,
            signer=signer,
            stamp_style=stamp.QRStampStyle(
                qr_inner_size=100,
                border_width=1,
                stamp_text=new_stamp_text,
                text_box_style=text.TextBoxStyle(
                    font=opentype.GlyphAccumulatorFactory(
                        staticfiles_storage.path("fonts/mirror82.otf")
                    ),
                    leading=12,
                    box_layout_rule=layout.SimpleBoxLayoutRule(
                        x_align=layout.AxisAlignment.ALIGN_MIN,
                        y_align=layout.AxisAlignment.ALIGN_MIN,
                        margins=layout.Margins(0,0,0,0)
                    )
                ),
                timestamp_format="%Y-%m-%d %H:%M:%S %Z",
                background=images.PdfImage(
                    staticfiles_storage.path("img/example.jpg")
                ),
                background_opacity=0.2
            ),
        )

        with open("SignWithText.pdf", "wb") as out_file:
            pdf_signer.sign_pdf(
                writer, output=out_file, appearance_text_params=cert_info
            )