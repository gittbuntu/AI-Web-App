odoo13 venv installed requirements

Babel	2.12.1	2.12.1
Jinja2	3.1.2	3.1.2
MarkupSafe	2.1.3	2.1.3
Pillow	10.0.1	10.0.1
PyPDF2	1.26.0	3.0.1
Werkzeug	0.16.0	2.3.7
XlsxWriter	1.1.2	3.1.5
attrbox	0.1.5	0.1.5
certifi	2023.7.22	2023.7.22
chardet	5.2.0	5.2.0
charset-normalizer	3.2.0	3.2.0
decorator	5.1.1	5.1.1
docopt	0.6.2	0.6.2
docutils	0.20.1	0.20.1
idna	3.4	3.4
libsass	0.22.0	0.22.0
lxml	4.9.3	4.9.3
num2words	0.5.6	0.5.12
passlib	1.7.4	1.7.4
pdfmerge	1.0.0	1.0.0
pip	23.2.1	23.2.1
polib	1.2.0	1.2.0
psutil	5.9.5	5.9.5
psycopg2	2.9.7	2.9.7
psycopg2-binary	2.9.7	2.9.7
pyparsing	2.2.0	3.1.1
pypdf	3.9.0	3.16.2
pyserial	3.4	3.5
python-dateutil	2.8.2	2.8.2
pytz	2023.3.post1	2023.3.post1
pyusb	1.0.2	1.2.1
pywin32	306	306
reportlab	4.0.5	4.0.5
requests	2.31.0	2.31.0
setuptools	65.5.1	68.2.2
six	1.16.0	1.16.0
tomli	2.0.1	2.0.1
urllib3	2.0.5	2.0.5
wheel	0.38.4	0.41.2
wkhtmltopdf	0.2	0.2
xlrd	1.1.0	2.0.1
xlwt	1.3.0	1.3.0

ERP Enthusiasts, ERP Consultants, Business Analysts, IT Professionals, Entrepreneurs and Business Owners
git config --list --global
---------------------------------------------------------------------------------------------
1. Senior Accountant -- basic setup (Chart of accounts, journals, taxes -- once setup complete and accounting is live then
	validating invoices and bills, processing payments, Generating legal reports)
2. Assistant Accountant (vendor bills, customer invoices, bank statements, payment follow-ups)
3. CFO -- monitor business wealth (Balance sheet, PL staement, analytic account, Budgets)
Note: 1,2,3 all are internal stack holders

4. Chartered accountant -- close taxes and fiscal year of the company(Review, adjustments, closing the journal entries)
5. Auditor -- Ensure that staements are trithful and fair 
6. Authorities -- deep control

----------------------------------------------------------------------------------------------
1. Chart of Account (its provided by the company as per requirement, its can be added through import)
2. Taxes (
	sales---- tax received (its a current liability), purchase---- tax receivable(its a current asset))
3. journals
4. Currencies
5. Analytic Accounts( Cost Center-Revenue Center)
6. Assets (create asset models for depriciation)
7. cut-off
8. create Deffered Revenue model(e.g: provide some warrenty of 12 or 14 months but devided this income into such months in this it is switable to automate as draft)
9. create Deffered Expence model (e.g: payement for something like early subscription but devided this amount into monthly expence)
----------------------------------------------------------------------------------------------------

1. Acc Receivable --- Income Acc (Invoice confirmed)--(PaymentStatus is NOT PAID)
2. Outstanding Receipts --- Receivable Acc (Register Payment)--(Status IN PAYMENT)
3. when create or upload bank statement (Bank Acc --- Suspence Acc) Now its ready to reconcile with invoice

-------------------------------------------------------------------------------------------------
"reflected" means gaour karna (e.g i have reflected on this)
"redundance" means faltoo






-------------------------------------------------------------------------------------------------

				Studio

Module (

	contains (
		Objects(models)
		Object Views
		Data Files
		Web Controllers))
Models (
	Logical structure of database
	Tables of data
	Linked to other tables)

Fields (
	Make the model
	Where data is stored
	Types- Basic (
			Simple Values
			Numbers,text,selection, etc),
		Relational (
			Link one model with onanother
			Important & common
				One2many
				Many2one
				Many2many))

Views (
	records are displayed
	Specified in xml
	customized independently for each model (FOrm, List, Kanban))

Menu (Button that execute an action)




------------


create customers list with complete deatil
give cards to customers for showing there identity on shops
create product categorry for this customers with specified discounts
deactive customer after one time use evry month

-----------------


1. create access rights for specific model
2. create user group ( connect group with access rights )
3. craete record rules ( connect group with record rule )

if we want to inherrit this group then
4. create new group ( connect parent group ID to this group ) by this all access rights and record rules work same for this group

if we want to provide seperate rule for this inherrited group then
5. create new record rule ( and provide new group Id in eval attribute)

NOte; domain_force is important in record rules we provide conditions in this attribute

(additional
6. technical>>> menu-item>>>> select model>>>> provide user group to see this in menu-item)

if we want to vissible or invisible any field by group then 
7. form_view>>> attribute(group)>>> put specific group ID (only this group memmbers can see this field), got id from group--debug---meta-data