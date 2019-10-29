# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-17 16:46
from __future__ import unicode_literals

import base.models
import core.model.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0031_auto_20190809_1103'),
        ('gatheros_subscription', '0024_subscription_buzzlead_campaign'),
        ('kanu_locations', '0001_initial'),
        ('payment', '0013_auto_20190828_2029'),
    ]

    operations = [
        migrations.CreateModel(
            name='Benefactor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_company', models.BooleanField(default=False, verbose_name='é pessoa juridica')),
                ('name', models.CharField(max_length=200, verbose_name='nome do pagador')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('U', 'Prefiro não definir')], default='M', max_length=1, null=True, verbose_name='sexo')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='data de nasc.')),
                ('email', models.EmailField(max_length=254, verbose_name='e-mail')),
                ('city_international', models.CharField(blank=True, help_text='Informe a cidade e estado ou província.', max_length=255, null=True, verbose_name='Cidade (Fora do Brasil)')),
                ('zip_code', models.CharField(blank=True, max_length=8, null=True, verbose_name='CEP')),
                ('zip_code_international', models.CharField(blank=True, max_length=50, null=True, verbose_name='CEP/Caixa Postal')),
                ('street', models.CharField(blank=True, help_text='Rua / Avenida / Viela / etc.', max_length=255, null=True, verbose_name='logradouro')),
                ('number', models.CharField(blank=True, help_text='Caso não tenha, informar S/N.', max_length=20, null=True, verbose_name='número')),
                ('complement', models.CharField(blank=True, max_length=255, null=True, verbose_name='complemento')),
                ('village', models.CharField(blank=True, max_length=255, null=True, verbose_name='bairro')),
                ('address_international', models.CharField(blank=True, max_length=255, null=True, verbose_name='endereço')),
                ('state_international', models.CharField(blank=True, max_length=255, null=True, verbose_name='estado')),
                ('country', models.CharField(blank=True, choices=[('AF', 'Afeganistão'), ('ZA', 'África Do Sul'), ('AL', 'Albânia'), ('DE', 'Alemanha'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antártida'), ('AG', 'Antígua E Barbuda'), ('AN', 'Antilhas Holandesas'), ('SA', 'Arábia Saudita'), ('DZ', 'Argélia'), ('AR', 'Argentina'), ('AM', 'Armênia'), ('AW', 'Aruba'), ('AU', 'Austrália'), ('AT', 'Áustria'), ('AZ  ', 'Azerbaijão'), ('BS', 'Bahamas'), ('BH', 'Bahrein'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Bélgica'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermudas'), ('BO', 'Bolívia'), ('BA', 'Bósnia-Herzegóvina'), ('BW', 'Botsuana'), ('BR', 'Brasil'), ('BN', 'Brunei'), ('BG', 'Bulgária'), ('BF', 'Burkina Fasso'), ('BI', 'Burundi'), ('BT', 'Butão'), ('CV', 'Cabo Verde'), ('CM', 'Camarões'), ('KH', 'Camboja'), ('CA', 'Canadá'), ('KZ', 'Cazaquistão'), ('TD', 'Chade'), ('CL', 'Chile'), ('CN', 'China'), ('CY', 'Chipre'), ('SG', 'Cingapura'), ('CO', 'Colômbia'), ('CG', 'Congo'), ('KP', 'Coréia Do Norte'), ('KR', 'Coréia Do Sul'), ('CI', 'Costa Do Marfim'), ('CR', 'Costa Rica'), ('HR', 'Croácia (Hrvatska)'), ('CU', 'Cuba'), ('DK', 'Dinamarca'), ('DJ', 'Djibuti'), ('DM', 'Dominica'), ('EG', 'Egito'), ('SV', 'El Salvador'), ('AE', 'Emirados Árabes Unidos'), ('EC', 'Equador'), ('ER', 'Eritréia'), ('SK', 'Eslováquia'), ('SI', 'Eslovênia'), ('ES', 'Espanha'), ('US', 'Estados Unidos'), ('EE', 'Estônia'), ('ET', 'Etiópia'), ('FJ', 'Fiji'), ('PH', 'Filipinas'), ('FI', 'Finlândia'), ('FR', 'França'), ('GA', 'Gabão'), ('GM', 'Gâmbia'), ('GH', 'Gana'), ('GE', 'Geórgia'), ('GI', 'Gibraltar'), ('GB', 'Reino Unido'), ('GD', 'Granada'), ('GR', 'Grécia'), ('GL', 'Groelândia'), ('GP', 'Guadalupe'), ('GU', 'Guam (Território Dos Estados Unidos)'), ('GT', 'Guatemala'), ('G', 'Guernsey'), ('GY', 'Guiana'), ('GF', 'Guiana Francesa'), ('GN', 'Guiné'), ('GQ', 'Guiné Equatorial'), ('GW', 'Guiné-Bissau'), ('HT', 'Haiti'), ('NL', 'Holanda'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungria'), ('YE', 'Iêmen'), ('IM', 'Ilha Do Homem'), ('CX', 'Ilha Natal'), ('PN', 'Ilha Pitcairn'), ('RE', 'Ilha Reunião'), ('AX', 'Ilhas Aland'), ('KY', 'Ilhas Cayman'), ('CC', 'Ilhas Cocos'), ('KM', 'Ilhas Comores'), ('CK', 'Ilhas Cook'), ('FO', 'Ilhas Faroes'), ('FK', 'Ilhas Falkland (Malvinas)'), ('GS', 'Ilhas Geórgia Do Sul E Sandwich Do Sul'), ('MP', 'Ilhas Marianas Do Norte'), ('MH', 'Ilhas Marshall'), ('NF', 'Ilhas Norfolk'), ('SC', 'Ilhas Seychelles'), ('SB', 'Ilhas Solomão'), ('SJ', 'Ilhas Svalbard E Jan Mayen'), ('TK', 'Ilhas Tokelau'), ('TC', 'Ilhas Turks E Caicos'), ('VI', 'Ilhas Virgens (Estados Unidos)'), ('VG', 'Ilhas Virgens (Inglaterra)'), ('WF', 'Ilhas Wallis E Futuna'), ('IN', 'Índia'), ('ID', 'Indonésia'), ('IR', 'Irã'), ('IQ', 'Iraque'), ('IE', 'Irlanda'), ('IS', 'Islândia'), ('IL', 'Israel'), ('IT', 'Itália'), ('JM', 'Jamaica'), ('JP', 'Japão'), ('JE', 'Jersey'), ('JO', 'Jordânia'), ('KE', 'Kênia'), ('KI', 'Kiribati'), ('KW', 'Kuait'), ('LA', 'Laos'), ('LV', 'Látvia'), ('LS', 'Lesoto'), ('LB', 'Líbano'), ('LR', 'Libéria'), ('LY', 'Líbia'), ('LI', 'Liechtenstein'), ('LT', 'Lituânia'), ('LU', 'Luxemburgo'), ('MO', 'Macau'), ('MK', 'Macedônia (República Yugoslava)'), ('MG', 'Madagascar'), ('MY', 'Malásia'), ('MW', 'Malaui'), ('MV', 'Maldivas'), ('ML', 'Mali'), ('MT', 'Malta'), ('MA', 'Marrocos'), ('MQ', 'Martinica'), ('MU', 'Maurício'), ('MR', 'Mauritânia'), ('YT', 'Mayotte'), ('MX', 'México'), ('FM', 'Micronésia'), ('MZ', 'Moçambique'), ('MD', 'Moldova'), ('MC', 'Mônaco'), ('MN', 'Mongólia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MM', 'Myanma'), ('NA', 'Namíbia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NI', 'Nicarágua'), ('NE', 'Níger'), ('NG', 'Nigéria'), ('NU', 'Niue'), ('NO', 'Noruega'), ('NC', 'Nova Caledônia'), ('NZ', 'Nova Zelândia'), ('OM', 'Omã'), ('PW', 'Palau'), ('PA', 'Panamá'), ('PG', 'Papua-Nova Guiné'), ('PK', 'Paquistão'), ('PY', 'Paraguai'), ('PE', 'Peru'), ('PF', 'Polinésia Francesa'), ('PL', 'Polônia'), ('PR', 'Porto Rico'), ('PT', 'Portugal'), ('QA', 'Qatar'), ('KG', 'Quirguistão'), ('CF', 'República Centro-Africana'), ('CD', 'República Democrática Do Congo'), ('DO', 'República Dominicana'), ('CZ', 'República Tcheca'), ('RO', 'Romênia'), ('RW', 'Ruanda'), ('RU', 'Rússia'), ('EH', 'Saara Ocidental'), ('VC', 'Saint Vincente E Granadinas'), ('AS', 'Samoa Americana'), ('WS', 'Samoa Ocidental'), ('SM', 'San Marino'), ('SH', 'Santa Helena'), ('LC', 'Santa Lúcia'), ('BL', 'São Bartolomeu'), ('KN', 'São Cristóvão E Névis'), ('MF', 'São Martim'), ('ST', 'São Tomé E Príncipe'), ('SN', 'Senegal'), ('SL', 'Serra Leoa'), ('RS', 'Sérvia'), ('SY', 'Síria'), ('SO', 'Somália'), ('LK', 'Sri Lanka'), ('PM', 'St. Pierre And Miquelon'), ('SZ', 'Suazilândia'), ('SD', 'Sudão'), ('SE', 'Suécia'), ('CH', 'Suíça'), ('SR', 'Suriname'), ('TJ', 'Tadjiquistão'), ('TH', 'Tailândia'), ('TW', 'Taiwan'), ('TZ', 'Tanzânia'), ('IO', 'Território Britânico Do Oceano Índico'), ('PS', 'Territórios Palestinos Ocupados'), ('TP', 'Timor Leste'), ('TG', 'Togo'), ('TO', 'Tonga'), ('TT', 'Trinidad And Tobago'), ('TN', 'Tunísia'), ('TM', 'Turcomenistão'), ('TR', 'Turquia'), ('TV', 'Tuvalu'), ('UA', 'Ucrânia'), ('UG', 'Uganda'), ('UY', 'Uruguai'), ('UZ', 'Uzbequistão'), ('VU', 'Vanuatu'), ('VA', 'Vaticano'), ('VE', 'Venezuela'), ('VN', 'Vietnã'), ('ZM', 'Zâmbia'), ('ZW', 'Zimbábue')], default='BR', max_length=10, verbose_name='país')),
                ('ddi', models.CharField(blank=True, choices=[('AF', '+93'), ('ZA', '+27'), ('AL', '+355'), ('DE', '+49'), ('AD', '+376'), ('AO', '+244'), ('AI', '+1264'), ('AQ', '+672'), ('AG', '+1268'), ('AN', '+599'), ('SA', '+966'), ('DZ', '+213'), ('AR', '+54'), ('AM', '+374'), ('AW', '+297'), ('AU', '+61'), ('AT', '+43'), ('AZ  ', '+994'), ('BS', '+1242'), ('BH', '+973'), ('BD', '+880'), ('BB', '+1246'), ('BY', '+375'), ('BE', '+32'), ('BZ', '+501'), ('BJ', '+229'), ('BM', '+1441'), ('BO', '+591'), ('BA', '+387'), ('BW', '+267'), ('BR', '+55'), ('BN', '+673'), ('BG', '+359'), ('BF', '+226'), ('BI', '+257'), ('BT', '+975'), ('CV', '+238'), ('CM', '+237'), ('KH', '+855'), ('CA', '+1'), ('KZ', '+77'), ('TD', '+235'), ('CL', '+56'), ('CN', '+86'), ('CY', '+537'), ('SG', '+65'), ('CO', '+57'), ('CG', '+242'), ('KP', '+850'), ('KR', '+82'), ('CI', '+225'), ('CR', '+506'), ('HR', '+385'), ('CU', '+53'), ('DK', '+45'), ('DJ', '+253'), ('DM', '+1767'), ('EG', '+20'), ('SV', '+503'), ('AE', '+971'), ('EC', '+593'), ('ER', '+291'), ('SK', '+421'), ('SI', '+386'), ('ES', '+34'), ('US', '+1'), ('EE', '+372'), ('ET', '+251'), ('FJ', '+679'), ('PH', '+63'), ('FI', '+358'), ('FR', '+33'), ('GA', '+241'), ('GM', '+220'), ('GH', '+233'), ('GE', '+995'), ('GI', '+350'), ('GB', '+44'), ('GD', '+1473'), ('GR', '+30'), ('GL', '+299'), ('GP', '+590'), ('GU', '+1671'), ('GT', '+502'), ('G', '+44'), ('GY', '+595'), ('GF', '+594'), ('GN', '+224'), ('GQ', '+240'), ('GW', '+245'), ('HT', '+509'), ('NL', '+31'), ('HN', '+504'), ('HK', '+852'), ('HU', '+36'), ('YE', '+967'), ('IM', '+44'), ('CX', '+61'), ('PN', '+872'), ('RE', '+262'), ('AX', ''), ('KY', '+345'), ('CC', '+61'), ('KM', '+269'), ('CK', '+682'), ('FO', '+298'), ('FK', '+500'), ('GS', '+500'), ('MP', '+1670'), ('MH', '+692'), ('NF', '+672'), ('SC', '+248'), ('SB', '+677'), ('SJ', '+47'), ('TK', '+690'), ('TC', '+1649'), ('VI', '+1340'), ('VG', '+1284'), ('WF', '+681'), ('IN', '+91'), ('ID', '+62'), ('IR', '+98'), ('IQ', '+964'), ('IE', '+353'), ('IS', '+354'), ('IL', '+972'), ('IT', '+39'), ('JM', '+1876'), ('JP', '+81'), ('JE', '+44'), ('JO', '+962'), ('KE', '+254'), ('KI', '+686'), ('KW', '+965'), ('LA', '+856'), ('LV', '+371'), ('LS', '+266'), ('LB', '+961'), ('LR', '+231'), ('LY', '+218'), ('LI', '+423'), ('LT', '+370'), ('LU', '+352'), ('MO', '+853'), ('MK', '+389'), ('MG', '+261'), ('MY', '+60'), ('MW', '+265'), ('MV', '+960'), ('ML', '+223'), ('MT', '+356'), ('MA', '+212'), ('MQ', '+596'), ('MU', '+230'), ('MR', '+222'), ('YT', '+262'), ('MX', '+52'), ('FM', '+691'), ('MZ', '+258'), ('MD', '+373'), ('MC', '+377'), ('MN', '+976'), ('ME', '+382'), ('MS', '+1664'), ('MM', '+95'), ('NA', '+264'), ('NR', '+674'), ('NP', '+977'), ('NI', '+505'), ('NE', '+227'), ('NG', '+234'), ('NU', '+683'), ('NO', '+47'), ('NC', '+687'), ('NZ', '+64'), ('OM', '+968'), ('PW', '+680'), ('PA', '+507'), ('PG', '+675'), ('PK', '+92'), ('PY', '+595'), ('PE', '+51'), ('PF', '+689'), ('PL', '+48'), ('PR', '+1939'), ('PT', '+351'), ('QA', '+974'), ('KG', '+996'), ('CF', '+236'), ('CD', '+243'), ('DO', '+1849'), ('CZ', '+420'), ('RO', '+40'), ('RW', '+250'), ('RU', '+7'), ('EH', '+212'), ('VC', '+1784'), ('AS', '+1684'), ('WS', '+685'), ('SM', '+378'), ('SH', '+290'), ('LC', '+1758'), ('BL', '+590'), ('KN', '+1869'), ('MF', '+590'), ('ST', '+239'), ('SN', '+221'), ('SL', '+232'), ('RS', '+381'), ('SY', '+963'), ('SO', '+252'), ('LK', '+94'), ('PM', '+508'), ('SZ', '+268'), ('SD', '+249'), ('SE', '+46'), ('CH', '+41'), ('SR', '+597'), ('TJ', '+992'), ('TH', '+66'), ('TW', '+886'), ('TZ', '+255'), ('IO', '+246'), ('PS', '+970'), ('TP', '+670'), ('TG', '+228'), ('TO', '+676'), ('TT', '+1868'), ('TN', '+216'), ('TM', '+993'), ('TR', '+90'), ('TV', '+688'), ('UA', '+380'), ('UG', '+256'), ('UY', '+598'), ('UZ', '+998'), ('VU', '+678'), ('VA', '+379'), ('VE', '+58'), ('VN', '+84'), ('ZM', '+260'), ('ZW', '+263')], default='BR', help_text='Código discagem do país.', max_length=10, verbose_name='DDI')),
                ('phone', models.CharField(max_length=50, verbose_name='celular')),
                ('cpf', models.CharField(blank=True, max_length=11, null=True, validators=[core.model.validators.cpf_validator], verbose_name='CPF')),
                ('cnpj', models.CharField(blank=True, help_text='CNPJ da empresa com a qual você está vinculado(a)', max_length=14, null=True, validators=[core.model.validators.cnpj_validator], verbose_name='CNPJ')),
                ('ein', models.CharField(blank=True, help_text='Employer ID Number', max_length=14, null=True, verbose_name='EIN/Tax ID')),
                ('doc_type', models.CharField(blank=True, choices=[('ID', 'ID'), ('Passport', 'Passport'), ('EIN', 'EIN')], help_text='Informe o tipo de documento.', max_length=11, null=True, verbose_name='tipo de documento')),
                ('doc_number', models.CharField(blank=True, help_text='Número de documento utilizado fora do Brasil.', max_length=80, null=True, verbose_name='Núm. Documento')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('beneficiary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='benefactors', to='gatheros_event.Person', verbose_name='pessoa')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kanu_locations.City', verbose_name='cidade-UF')),
            ],
            options={
                'verbose_name_plural': 'benfeitores',
                'verbose_name': 'benfeitor',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Payer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('benefactor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payers', to='payment.Benefactor', verbose_name='benfeitor')),
                ('lot', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='payers', to='gatheros_subscription.Lot', verbose_name='lote')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payers', to='gatheros_subscription.Subscription', verbose_name='inscrição')),
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payer', to='payment.Transaction', verbose_name='transaction')),
            ],
            options={
                'verbose_name_plural': 'pagadores de inscrição',
                'verbose_name': 'pagador de inscrição',
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='payer',
            unique_together=set([('benefactor', 'subscription', 'transaction')]),
        ),
    ]