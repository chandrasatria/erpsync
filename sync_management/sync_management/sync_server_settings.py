# -*- coding: utf-8 -*-
# Copyright (c) 2015, erpx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappeclient import FrappeClient
import json

class SyncServerSettings(Document):
	pass
	
@frappe.whitelist()
def sync_role_master(self, method):
	# /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/role row 14, after insert WARNING
	server_tujuan = frappe.db.get_single_value("Sync Server Settings", "server_tujuan")
	clientroot = FrappeClient(server_tujuan, "Administrator", "admin")
	docu_tujuan = clientroot.get_value(self.doctype, "name", {"name":self.name})
	doc = frappe.get_doc(self.doctype, self.name)
	pr_doc = {}
	pr_doc.update({ "doctype": "Role" })
	pr_doc.update({ "role_name": doc.role_name })
	if docu_tujuan:
		clientroot.update(pr_doc)
	else:
		clientroot.insert(pr_doc)

@frappe.whitelist()
def sync_master_after_submit(self, method):
	server_tujuan = frappe.db.get_single_value("Sync Server Settings", "server_tujuan")
	clientroot = FrappeClient(server_tujuan, "Administrator", "admin")

	# frappe.throw(clientroot.get_doc("Company","Jungle"))
	docu_tujuan = clientroot.get_value(self.doctype, "name", {"name":self.name})

	doc = frappe.get_doc(self.doctype, self.name)

	kolom_parent_after_submit = frappe.db.sql(""" SELECT td.fieldname
	FROM `tabDocField` td
	WHERE parent = "{}" 
	AND allow_on_submit = 1
	GROUP BY td.`fieldname`
	ORDER BY OPTIONS; """.format(self.doctype))

	pr_doc = {}
	for rowkolom in kolom_parent_after_submit:
		if str(rowkolom[0]) != "docstatus":
			if str(doc.get(str(rowkolom[0]))) != "None" :
				if not docu_tujuan:
					pr_doc.update({ (rowkolom[0]) : str(doc.get(str(rowkolom[0]))) })
				elif str(rowkolom[0]) != "creation" and str(rowkolom[0]) != "modified":
					pr_doc.update({ (rowkolom[0]) : str(doc.get(str(rowkolom[0]))) })

	pr_doc.update({ "doctype": doc.doctype })
	pr_doc.update({ "name": doc.name })
	# pr_doc_items = []
	# for temp_baris_item in self.uoms :
	# 	pr_doc_items.append({
	# 		"uom" : temp_baris_item.uom,
	# 		"conversion_factor" : temp_baris_item.conversion_factor,

	# 	})
	# pr_doc.update({ "uoms": pr_doc_items })
	# stringdoc = (str(pr_doc)).replace(" u'","'")
	# stringdoc = stringdoc.replace("'", '"')
	# stringdoc = stringdoc.replace("'", '"')
	# stringdoc = stringdoc.replace("{u", "{")

	# frappe.throw(stringdoc) 
	# d = json.dumps(stringdoc)
	
	# frappe.throw(str(pr_doc))

	docu_tujuan = clientroot.get_value(self.doctype, "name", {"name":self.name})
	if docu_tujuan:
		clientroot.update(pr_doc)
	else:
		clientroot.insert(pr_doc)

@frappe.whitelist()
def sync_master(self, method):


	server_tujuan = frappe.db.get_single_value("Sync Server Settings", "server_tujuan")
	clientroot = FrappeClient(server_tujuan, "Administrator", "admin")

	# frappe.throw(clientroot.get_doc("Company","Jungle"))
	docu_tujuan = clientroot.get_value(self.doctype, "name", {"name":self.name})
	
	doc = frappe.get_doc(self.doctype, self.name)
	

	if doc.get("docstatus") == 1:
		return

	if doc.get("amended_from"):
		return

	kolom_parent = frappe.db.sql(""" SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='tab{}' """.format(self.doctype))

	kolom_child = frappe.db.sql(""" SELECT td.fieldname, td.options
		FROM `tabDocField` td
		WHERE parent = "{}" AND fieldtype = "Table" 
		GROUP BY td.`fieldname`
		ORDER BY OPTIONS;
		 """.format(self.doctype))
	
	kolom_table = frappe.db.sql("""SELECT td.fieldname, ic.COLUMN_NAME, ic.DATA_TYPE  FROM `tabDocField` td 
		JOIN INFORMATION_SCHEMA.COLUMNS ic ON CONCAT("tab",td.`options`) = ic.`TABLE_NAME`
		WHERE parent = "{}" AND fieldtype = "Table"
		ORDER BY OPTIONS """.format(self.doctype))
	

	pr_doc = {}

	# for temp_baris_item in self.get("uoms") :
	# 	tampungan = temp_baris_item.get("uom")
	# 	frappe.throw(str(tampungan))
	
	for rowkolom in kolom_parent:
		if str(rowkolom[0]) != "docstatus":
			if str(doc.get(str(rowkolom[0]))) != "None" :
				if str(rowkolom[1]) == "date" or str(rowkolom[1]) == "datetime" or str(rowkolom[1]) == "time" :
					if not docu_tujuan:
						pr_doc.update({ (rowkolom[0]) : str(doc.get(str(rowkolom[0]))) })
					elif str(rowkolom[0]) != "creation" and str(rowkolom[0]) != "modified":
						pr_doc.update({ (rowkolom[0]) : str(doc.get(str(rowkolom[0]))) })

				else:
					pr_doc.update({ (rowkolom[0]) : (doc.get(str(rowkolom[0]))) })

	for rowkolom in kolom_child:
		if self.get(rowkolom[0]):
			pr_doc_items = []
			for rowtable in self.get(rowkolom[0]):
				pr_doc_child = {}
				# frappe.throw(str(rowtable.get("uom")))
				for rowbaris in kolom_table:

					if rowbaris[0] == rowkolom[0]:
						if str(rowbaris[1]) != "docstatus" and str(rowbaris[1]) != "name":
							if str(rowtable.get(str(rowbaris[1]))) != "None" :
								if str(rowbaris[2]) == "date" or str(rowbaris[2]) == "datetime" or str(rowbaris[2]) == "time" :
									if not docu_tujuan:
										pr_doc_child.update({ rowbaris[1] : str(rowtable.get(str(rowbaris[1]))) })
									elif str(rowbaris[1]) != "creation" and str(rowbaris[1]) != "modified":
										pr_doc_child.update({ rowbaris[1] : str(rowtable.get(str(rowbaris[1]))) })
								else:
									pr_doc_child.update({ rowbaris[1] : (rowtable.get(str(rowbaris[1]))) })
				pr_doc_items.append(pr_doc_child)					
			# frappe.throw(str(pr_doc_items))
			pr_doc.update({ rowkolom[0]: pr_doc_items })
	
	pr_doc.update({ "doctype": doc.doctype })
	# pr_doc_items = []
	# for temp_baris_item in self.uoms :
	# 	pr_doc_items.append({
	# 		"uom" : temp_baris_item.uom,
	# 		"conversion_factor" : temp_baris_item.conversion_factor,

	# 	})
	# pr_doc.update({ "uoms": pr_doc_items })
	# stringdoc = (str(pr_doc)).replace(" u'","'")
	# stringdoc = stringdoc.replace("'", '"')
	# stringdoc = stringdoc.replace("'", '"')
	# stringdoc = stringdoc.replace("{u", "{")

	# frappe.throw(stringdoc) 
	# d = json.dumps(stringdoc)
	
	docu_tujuan = clientroot.get_value(self.doctype, "name", {"name":self.name})
	if docu_tujuan:
		clientroot.update(pr_doc)
	else:
		clientroot.insert(pr_doc)

@frappe.whitelist()
def sync_save_document(self, method):
	if self.is_sync == 0:
		return

	server_tujuan = frappe.db.get_single_value("Sync Server Settings", "server_tujuan")
	clientroot = FrappeClient(server_tujuan, "Administrator", "admin")

	# frappe.throw(clientroot.get_doc("Company","Jungle"))
	docu_tujuan = clientroot.get_value(self.doctype, "name", {"name":self.name})
	
	doc = frappe.get_doc(self.doctype, self.name)
	if doc.get("amended_from"):
		return

	kolom_parent = frappe.db.sql(""" SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='tab{}' """.format(self.doctype))

	kolom_child = frappe.db.sql(""" SELECT td.fieldname, td.options
		FROM `tabDocField` td
		WHERE parent = "{}" AND fieldtype = "Table" 
		GROUP BY td.`fieldname`
		ORDER BY OPTIONS;
		 """.format(self.doctype))
	
	kolom_table = frappe.db.sql("""SELECT td.fieldname, ic.COLUMN_NAME, ic.DATA_TYPE  FROM `tabDocField` td 
		JOIN INFORMATION_SCHEMA.COLUMNS ic ON CONCAT("tab",td.`options`) = ic.`TABLE_NAME`
		WHERE parent = "{}" AND fieldtype = "Table"
		ORDER BY OPTIONS """.format(self.doctype))
	
	pr_doc = {}

	# for temp_baris_item in self.get("uoms") :
	# 	tampungan = temp_baris_item.get("uom")
	# 	frappe.throw(str(tampungan))
	
	for rowkolom in kolom_parent:
		if str(rowkolom[0]) != "docstatus" and str(rowkolom[0]) != "other_charges_calculation":
			if str(doc.get(str(rowkolom[0]))) != "None" :
				if str(rowkolom[1]) == "date" or str(rowkolom[1]) == "datetime" or str(rowkolom[1]) == "time" :
					if not docu_tujuan:
						pr_doc.update({ (rowkolom[0]) : str(doc.get(str(rowkolom[0]))) })
					elif str(rowkolom[0]) != "creation" and str(rowkolom[0]) != "modified":
						pr_doc.update({ (rowkolom[0]) : str(doc.get(str(rowkolom[0]))) })

				else:
					pr_doc.update({ (rowkolom[0]) : (doc.get(str(rowkolom[0]))) })

	for rowkolom in kolom_child:
		if self.get(rowkolom[0]):
			pr_doc_items = []
			for rowtable in self.get(rowkolom[0]):
				pr_doc_child = {}
				for rowbaris in kolom_table:

					if rowbaris[0] == rowkolom[0]:
						if str(rowbaris[1]) != "docstatus" and str(rowbaris[1]) != "name":
							if str(rowtable.get(str(rowbaris[1]))) != "None" :
								if str(rowbaris[2]) == "date" or str(rowbaris[2]) == "datetime" or str(rowbaris[2]) == "time" :
									if not docu_tujuan:
										pr_doc_child.update({ rowbaris[1] : str(rowtable.get(str(rowbaris[1]))) })
									elif str(rowbaris[1]) != "creation" and str(rowbaris[1]) != "modified":
										pr_doc_child.update({ rowbaris[1] : str(rowtable.get(str(rowbaris[1]))) })
								else:
									pr_doc_child.update({ rowbaris[1] : (rowtable.get(str(rowbaris[1]))) })
						elif str(rowbaris[1]) == "name":
							pr_doc_child.update({ "tampungan_awal" : rowtable.get(str(rowbaris[1])) })

				pr_doc_items.append(pr_doc_child)
			pr_doc.update({ rowkolom[0]: pr_doc_items })
	
	pr_doc.update({ "doctype": doc.doctype })
	# pr_doc.update({ "uoms": pr_doc_items })
	# stringdoc = (str(pr_doc)).replace(" u'","'")
	# stringdoc = stringdoc.replace("'", '"')
	# stringdoc = stringdoc.replace("'", '"')
	# stringdoc = stringdoc.replace("{u", "{")

	# frappe.throw(stringdoc)
	# d = json.dumps(stringdoc)
	
	# frappe.throw(str(pr_doc))
	# docu_tujuan = clientroot.get_value(self.doctype, "name", {"name":self.name})
	if docu_tujuan:
		clientroot.update(pr_doc)
	else:
		clientroot.insert(pr_doc)

@frappe.whitelist()
def sync_submit_document(self, method):
	if self.is_sync == 0:
		return

	if self.get("amended_from"):
		return
	server_tujuan = frappe.db.get_single_value("Sync Server Settings", "server_tujuan")
	clientroot = FrappeClient(server_tujuan, "Administrator", "admin")
	docu_tujuan = clientroot.get_value(self.doctype, "name", {"name":self.name})
	if docu_tujuan:
		pr_doc = clientroot.get_doc(self.doctype,self.name)

		clientroot.submit(pr_doc)
		
@frappe.whitelist()
def sync_submit_master(self, method):
	if self.get("amended_from"):
		return
	server_tujuan = frappe.db.get_single_value("Sync Server Settings", "server_tujuan")
	clientroot = FrappeClient(server_tujuan, "Administrator", "admin")
	docu_tujuan = clientroot.get_value(self.doctype, "name", {"name":self.name})
	if docu_tujuan:
		pr_doc = clientroot.get_doc(self.doctype,self.name)

		clientroot.submit(pr_doc)

@frappe.whitelist()
def sync_autoname (self, method):
	if self.is_sync == 0:
		return

	check_nama = frappe.get_all('Custom Sync Naming', filters={'name': self.doctype}, fields=['name'])

	if not check_nama:
		frappe.throw("Silahkan mengisi series untuk dokumen {} di sync ini di Custom Sync Naming.".format(self.doctype))
	else:	
		nama_series = frappe.get_doc("Custom Sync Naming", self.doctype)
		from frappe.model.naming import make_autoname
		self.name = make_autoname(nama_series.sync_naming_series)