from __future__ import unicode_literals

import frappe
from frappe import scrub
from textwrap import wrap
from frappe.utils import add_to_date, nowdate,nowtime
from datetime import timedelta
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt
from frappe import _
# from erpnext.accounts.utils import get_fiscal_year, now
from erpnext.setup.doctype.item_group.item_group import get_child_item_groups

@frappe.whitelist()
def create_lead(business_name,first_name,last_name,address,city,state,zipcode,website,email_address,telephone_number,territory,source=None,organization_lead=None,notes=None):

	if territory:
		if frappe.db.exists("Territory", territory):
			territory=territory
		else:
			territory='United States'
	else:
		territory='United States'

	if organization_lead!=None:
		organization_lead=organization_lead
	else:
		organization_lead=1
	
	if 	notes!=None:
		notes=notes
	else:
		notes=''

	if 	source!=None:
		source=source
	else:
		source="Wholesale Inquiry form"

	# hard coded values
	lead_owner="ahmed@zomoamerica.com"
	# lead_owner="ashish@greycube.in"
	request_type="Product Enquiry"
	country="United States"
	status="Lead"
	organization_lead=organization_lead
	company = frappe.db.get_single_value('Global Defaults', 'default_company')
	address_type="Billing"
	source=source
	contact_by="ahmed@zomoamerica.com"
	last_followup_date=add_to_date(nowdate(), months=0, days=7)
	first_followup_date=add_to_date(nowdate(), months=0, days=1)

	lead_map={
	"company_name":business_name,
	"website":website,
	"organization_lead":organization_lead,
	"status":status,
	"request_type":request_type,
	"company":company,
	"lead_owner":lead_owner,
	"territory":territory,
	"source":source,
	"contact_by":contact_by,
	"contact_date":first_followup_date,
	"ends_on":last_followup_date,
	"notes":notes
	}

	# Check if existing lead
	lead_name = None
	if email_address:
		lead_name = frappe.db.get_value("Lead", {"email_id": email_address})
		if not lead_name:
			lead_map.update({"email_id":email_address})

	if not lead_name and telephone_number:
		lead_name = frappe.db.get_value("Lead", {"phone": telephone_number})
		if not lead_name:
			lead_map.update({"phone":telephone_number})	

	if not lead_name:
		#new
		lead_name=frappe.scrub(first_name)+' '+frappe.scrub(last_name)
		lead_map.update({"lead_name":lead_name})	
		lead = frappe.new_doc("Lead")
		lead.update(lead_map)
		lead.insert(ignore_permissions=True)
		print(lead.name,"new lead")
	else:
		#existing lead
		lead=frappe.get_doc("Lead", lead_name)
		lead.update(lead_map)
		lead.save(ignore_permissions=True)
		print(lead.name,"existing lead")
	frappe.db.commit()

	address_list=wrap(address,40)
	print(len(address_list),'len(address_list)')
	if len(address_list)>1:
		address_line2=address_list[1]
		address_line1=address_list[0]+','
	else:
		address_line1=address_list[0]
		address_line2=None

	address_map={
		"address_line1":address_line1,
		"address_line2":address_line2,
		"address_type":address_type,
		"city":city,
		"state":state,
		"pincode":zipcode,
		"email_id":email_address,
		"phone":telephone_number,
		"country":country
	}
#check if existing address
	address_name=lead_name+"-"+address_type
	if frappe.db.exists("Address", address_name):
		address=frappe.get_doc("Address", address_name)
		address.update(address_map)
		address.save(ignore_permissions=True)
		print(address.name,"address existing")
	else:
		address = frappe.new_doc("Address")
		address.update(address_map)
		lead_link={
			"link_doctype":"Lead",
			"link_name":lead.name,
			"link_title":lead.name
		}
		address.append("links",lead_link)
		address.insert(ignore_permissions=True)
		print(address.name,"address new")
	frappe.db.commit()



def copy_shipping_details_from_item_to_SI(self,method):
	if self.items:
		if self.items[0]:
			if self.items[0].delivery_note:
				delivery_note=self.items[0].delivery_note
				shipping_method_za,shipment_tracking_no_za,	no_of_boxes_za = frappe.db.get_value('Delivery Note', delivery_note, ['shipping_method_za', 'shipment_tracking_no_za','no_of_boxes_za'])
				self.shipping_method_za=shipping_method_za
				self.shipment_tracking_no_za=shipment_tracking_no_za
				self.no_of_boxes_za=no_of_boxes_za
			

def calculate_total_tobacco_weight(self,method):
	self.total_tobacco_weight_za=0
	for item in self.items:
		if item.item_group =='TOBACCO':
			self.total_tobacco_weight_za+=item.total_weight
		else:
			item_group = frappe.get_doc("Item Group", item.item_group)
			parent_groups = frappe.db.sql("""select name from `tabItem Group`
			where lft <= %s and rgt >= %s
			and name = 'TOBACCO'
			order by lft asc""", (item_group.lft, item_group.rgt), as_list=True)
			if parent_groups:
				parent_tobacco_group=parent_groups[0][0]
				if parent_tobacco_group:
					self.total_tobacco_weight_za+=item.total_weight
	if self.doctype =='Sales Invoice' and self.is_return == 1 and self.total_tobacco_weight_za > 0:
		self.total_tobacco_weight_za = self.total_tobacco_weight_za * -1	

def update_delivery_note_workflow_state(self,method):
	if self.status == 'Completed' and self.workflow_state != 'Completed':
		self.db_set('workflow_state', self.status, update_modified = True)


# def delete_connected_stock_entry(self,method):
# 	if frappe.db.exists("Stock Entry", self.stock_entry_cf):
# 		frappe.delete_doc("Stock Entry", self.stock_entry_cf)
# 		frappe.msgprint(_("Stock Entry  {0} connected with this Delivery Note is deleted.").format(self.stock_entry_cf))		


def delink_connected_stock_entry(self,method):
	if self.stock_entry_cf:
		frappe.db.set_value('Delivery Note', self.name, 'stock_entry_cf', '')

@frappe.whitelist()
def create_stock_entry(source_name, target_doc=None):
	found_item=False
	delivery_note=frappe.get_doc('Delivery Note',source_name)
	stock_entry=frappe.new_doc("Stock Entry")
	stock_entry.stock_entry_type = "Repack"
	stock_entry.posting_date= nowdate()
	stock_entry.posting_time=nowtime()

	for source_item in delivery_note.get("items"):
		master_case_item_cf=frappe.db.get_value('Item', source_item.item_code, 'master_case_item_cf')
		if source_item.qty > source_item.actual_qty and master_case_item_cf:
			master_case_item_exists_in_source_table=False
			for check_source_item in delivery_note.get("items"):
				if check_source_item.item_code==master_case_item_cf:
					master_case_item_exists_in_source_table=True
					master_case_item_qty_status=flt(check_source_item.actual_qty-check_source_item.qty)
					break
			if(master_case_item_exists_in_source_table==True and master_case_item_qty_status>1) or (master_case_item_exists_in_source_table==False):
				target_item_master = stock_entry.append('items', {})
				target_item_master.item_code=master_case_item_cf
				target_item_master.s_warehouse = source_item.warehouse
				target_item_master.qty=flt(1)	
				target_item = stock_entry.append('items', {})
				target_item.item_code=source_item.item_code
				target_item.t_warehouse = source_item.warehouse
				if source_item.uom=="BOX" and source_item.item_name.find("250GM"):
					target_item.qty=flt(24)
				elif source_item.uom=="CARTON" and source_item.item_name.find("50GM"):
					target_item.qty=flt(12)
				found_item=True
	if found_item==True:
		stock_entry.run_method("set_missing_values")
		stock_entry.run_method("calculate_rate_and_amount")
		stock_entry.save()
		delivery_note.stock_entry_cf=stock_entry.name
		delivery_note.save()
		return stock_entry	
	else:
		return "There are no eligibile items for making stock entry."



@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		qty = flt(flt(obj.stock_qty) - flt(obj.ordered_qty))/ target.conversion_factor \
			if flt(obj.stock_qty) > flt(obj.ordered_qty) else 0
		target.qty = qty
		target.transfer_qty = qty * obj.conversion_factor
		target.conversion_factor = obj.conversion_factor

		if source_parent.material_request_type == "Material Transfer" or source_parent.material_request_type == "Customer Provided" :
			target.t_warehouse = obj.warehouse
		elif source_parent.material_request_type == "Withdrawal Request":
			target.t_warehouse = frappe.db.get_single_value('Stock Settings', 'default_warehouse')
		else:
			target.s_warehouse = obj.warehouse

		if source_parent.material_request_type == "Customer Provided":
			target.allow_zero_valuation_rate = 1

	def set_missing_values(source, target):
		target.purpose = source.material_request_type
		if source.job_card:
			target.purpose = 'Material Transfer for Manufacture'

		if source.material_request_type == "Customer Provided":
			target.purpose = "Material Receipt"

		if source.material_request_type == "Withdrawal Request":
			target.purpose = "Material Transfer"

		target.run_method("calculate_rate_and_amount")
		target.set_stock_entry_type()
		target.set_job_card_data()

	doclist = get_mapped_doc("Material Request", source_name, {
		"Material Request": {
			"doctype": "Stock Entry",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["in", ["Material Transfer", "Material Issue", "Customer Provided","Withdrawal Request"]]
			}
		},
		"Material Request Item": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				"name": "material_request_item",
				"parent": "material_request",
				"uom": "stock_uom"
			},
			"postprocess": update_item,
			"condition": lambda doc: doc.ordered_qty < doc.stock_qty
		}
	}, target_doc, set_missing_values)

	return doclist		

# def set_title_for_material_request(self,method):
# 	if self.material_request_type == 'Withdrawal Request':
# 		self.title = _('Material Withdrawal INV {0}').format(self.sales_invoice_cf)[:100]
# 	if self.material_request_type == 'Withdrawal Request':
# 		self.title = _('Material Withdrawal INV {0}').format(self.sales_invoice_cf)[:100]		

@frappe.whitelist()
def stock_entry_calculate_total_tobacoo_weight(doc):
	doc=frappe._dict(frappe.parse_json(doc))
	valid_item_groups=get_child_item_groups('TOBACCO')
	stock_entry= frappe.get_doc('Stock Entry', doc.name)
	se_items=stock_entry.get("items")
	total_tobacco_weight_cf=0
	if stock_entry.purpose =='Material Transfer':
		for item in se_items:
			if item.item_group in valid_item_groups:
				weight_per_unit = frappe.db.get_value('Item', item.item_code, 'weight_per_unit')
				total_tobacco_weight_cf+=flt(item.qty*weight_per_unit)
		stock_entry.total_tobacco_weight_cf=total_tobacco_weight_cf
		stock_entry.save()
		return 1

@frappe.whitelist()
def zomo_sales_invoice_validate(self,method):
	calculate_total_tobacco_weight(self,method)
	copy_shipping_details_from_item_to_SI(self,method)