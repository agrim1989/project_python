# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ShipmentInformation'
        db.create_table('amazon_api_shipmentinformation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('TransactionInformation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='am_t_info', to=orm['amazon_api.TransactionInformation'])),
            ('EdiDocumentInformation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='am_e_d_info', to=orm['amazon_api.EdiDocumentInformation'])),
            ('when_created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('when_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('amazon_api', ['ShipmentInformation'])

        # Adding model 'TransactionInformation'
        db.create_table('amazon_api_transactioninformation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('SenderIdentifier', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('recipientidentifier', self.gf('django.db.models.fields.CharField')(default='AMAZON', max_length=6)),
            ('DateOfPreparation', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('TimeOfPreparation', self.gf('django.db.models.fields.CharField')(max_length=6)),
        ))
        db.send_create_signal('amazon_api', ['TransactionInformation'])

        # Adding model 'EdiDocumentInformation'
        db.create_table('amazon_api_edidocumentinformation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('EdiDocumentStandard', self.gf('django.db.models.fields.CharField')(default='X12', max_length=3)),
            ('EdiDocumentName', self.gf('django.db.models.fields.CharField')(default='XML', max_length=3)),
            ('EdiDocumentVersion', self.gf('django.db.models.fields.FloatField')(default='1.1', max_length=3)),
        ))
        db.send_create_signal('amazon_api', ['EdiDocumentInformation'])

        # Adding model 'ItemInformation'
        db.create_table('amazon_api_iteminformation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('itemid', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('cartonquantity', self.gf('django.db.models.fields.IntegerField')(max_length=15)),
            ('palletquantity', self.gf('django.db.models.fields.IntegerField')(max_length=15)),
        ))
        db.send_create_signal('amazon_api', ['ItemInformation'])

        # Adding model 'ShipmentStatus'
        db.create_table('amazon_api_shipmentstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipment_info', self.gf('django.db.models.fields.related.ForeignKey')(related_name='am_ship_info', to=orm['amazon_api.ShipmentIdentification'])),
            ('appointmentstatus', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('appointmentstatusreason', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('recipientidentifier', self.gf('django.db.models.fields.CharField')(default='AMAZON', max_length=6)),
            ('stagecode', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('trailernumber', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('transportmode', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('carrierscac', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('sealnumber', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('purchaseordernumber', self.gf('django.db.models.fields.IntegerField')(max_length=30, null=True, blank=True)),
            ('datetimeperiodcode', self.gf('django.db.models.fields.related.ForeignKey')(related_name='am_dtpc', to=orm['amazon_api.EstimatedDeliveryDateTime'])),
            ('equipmentcode', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('equipmenttype', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('measurementcode', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('measurementvalue', self.gf('django.db.models.fields.IntegerField')(max_length=20, null=True, blank=True)),
            ('grossweightuom', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('grossweightvalue', self.gf('django.db.models.fields.FloatField')(max_length=20, null=True, blank=True)),
            ('measurementinformation', self.gf('django.db.models.fields.TextField')(max_length=20, null=True, blank=True)),
            ('iteminformation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['amazon_api.ItemInformation'])),
            ('referenceid', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('referenceidtype', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('handlingcode', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('specialservicescode', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('handlingdescription', self.gf('django.db.models.fields.TextField')(max_length=20, null=True, blank=True)),
            ('ladingexceptioncode', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('packagingformcode', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('ladingquantity', self.gf('django.db.models.fields.IntegerField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal('amazon_api', ['ShipmentStatus'])

        # Adding model 'ShipmentIdentification'
        db.create_table('amazon_api_shipmentidentification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('messagereferencenum', self.gf('django.db.models.fields.IntegerField')(max_length=15)),
            ('shipmentidentifier', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='am_shipment', null=True, to=orm['service_centre.Shipment'])),
            ('amazonreferencenumber', self.gf('django.db.models.fields.IntegerField')(max_length=15)),
            ('shipmentinformation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['amazon_api.ShipmentInformation'])),
        ))
        db.send_create_signal('amazon_api', ['ShipmentIdentification'])

        # Adding model 'EstimatedDeliveryDateTime'
        db.create_table('amazon_api_estimateddeliverydatetime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetimeperiodcode', self.gf('django.db.models.fields.IntegerField')(default=203)),
            ('estimateddeliverydatetimetz', self.gf('django.db.models.fields.CharField')(default='IST', max_length=3)),
            ('estimateddeliverydatetimeformat', self.gf('django.db.models.fields.CharField')(default='YYYYMMDDHHMMSS', max_length=18)),
            ('estimateddeliverydatetimevalue', self.gf('django.db.models.fields.DateTimeField')(max_length=14)),
        ))
        db.send_create_signal('amazon_api', ['EstimatedDeliveryDateTime'])


    def backwards(self, orm):
        # Deleting model 'ShipmentInformation'
        db.delete_table('amazon_api_shipmentinformation')

        # Deleting model 'TransactionInformation'
        db.delete_table('amazon_api_transactioninformation')

        # Deleting model 'EdiDocumentInformation'
        db.delete_table('amazon_api_edidocumentinformation')

        # Deleting model 'ItemInformation'
        db.delete_table('amazon_api_iteminformation')

        # Deleting model 'ShipmentStatus'
        db.delete_table('amazon_api_shipmentstatus')

        # Deleting model 'ShipmentIdentification'
        db.delete_table('amazon_api_shipmentidentification')

        # Deleting model 'EstimatedDeliveryDateTime'
        db.delete_table('amazon_api_estimateddeliverydatetime')


    models = {
        'amazon_api.edidocumentinformation': {
            'EdiDocumentName': ('django.db.models.fields.CharField', [], {'default': "'XML'", 'max_length': '3'}),
            'EdiDocumentStandard': ('django.db.models.fields.CharField', [], {'default': "'X12'", 'max_length': '3'}),
            'EdiDocumentVersion': ('django.db.models.fields.FloatField', [], {'default': "'1.1'", 'max_length': '3'}),
            'Meta': {'object_name': 'EdiDocumentInformation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'amazon_api.estimateddeliverydatetime': {
            'Meta': {'object_name': 'EstimatedDeliveryDateTime'},
            'datetimeperiodcode': ('django.db.models.fields.IntegerField', [], {'default': '203'}),
            'estimateddeliverydatetimeformat': ('django.db.models.fields.CharField', [], {'default': "'YYYYMMDDHHMMSS'", 'max_length': '18'}),
            'estimateddeliverydatetimetz': ('django.db.models.fields.CharField', [], {'default': "'IST'", 'max_length': '3'}),
            'estimateddeliverydatetimevalue': ('django.db.models.fields.DateTimeField', [], {'max_length': '14'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'amazon_api.iteminformation': {
            'Meta': {'object_name': 'ItemInformation'},
            'cartonquantity': ('django.db.models.fields.IntegerField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itemid': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'palletquantity': ('django.db.models.fields.IntegerField', [], {'max_length': '15'})
        },
        'amazon_api.shipmentidentification': {
            'Meta': {'object_name': 'ShipmentIdentification'},
            'amazonreferencenumber': ('django.db.models.fields.IntegerField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'messagereferencenum': ('django.db.models.fields.IntegerField', [], {'max_length': '15'}),
            'shipmentidentifier': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'am_shipment'", 'null': 'True', 'to': "orm['service_centre.Shipment']"}),
            'shipmentinformation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['amazon_api.ShipmentInformation']"})
        },
        'amazon_api.shipmentinformation': {
            'EdiDocumentInformation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'am_e_d_info'", 'to': "orm['amazon_api.EdiDocumentInformation']"}),
            'Meta': {'object_name': 'ShipmentInformation'},
            'TransactionInformation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'am_t_info'", 'to': "orm['amazon_api.TransactionInformation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'when_created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'when_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'amazon_api.shipmentstatus': {
            'Meta': {'object_name': 'ShipmentStatus'},
            'appointmentstatus': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'appointmentstatusreason': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'carrierscac': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'datetimeperiodcode': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'am_dtpc'", 'to': "orm['amazon_api.EstimatedDeliveryDateTime']"}),
            'equipmentcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'equipmenttype': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'grossweightuom': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'grossweightvalue': ('django.db.models.fields.FloatField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'handlingcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'handlingdescription': ('django.db.models.fields.TextField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iteminformation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['amazon_api.ItemInformation']"}),
            'ladingexceptioncode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'ladingquantity': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'measurementcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'measurementinformation': ('django.db.models.fields.TextField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'measurementvalue': ('django.db.models.fields.IntegerField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'packagingformcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'purchaseordernumber': ('django.db.models.fields.IntegerField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'recipientidentifier': ('django.db.models.fields.CharField', [], {'default': "'AMAZON'", 'max_length': '6'}),
            'referenceid': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'referenceidtype': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'sealnumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'shipment_info': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'am_ship_info'", 'to': "orm['amazon_api.ShipmentIdentification']"}),
            'specialservicescode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'stagecode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'trailernumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'transportmode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'amazon_api.transactioninformation': {
            'DateOfPreparation': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'Meta': {'object_name': 'TransactionInformation'},
            'SenderIdentifier': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'TimeOfPreparation': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipientidentifier': ('django.db.models.fields.CharField', [], {'default': "'AMAZON'", 'max_length': '6'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'authentication.department': {
            'Meta': {'object_name': 'Department'},
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'authentication.employeemaster': {
            'Meta': {'object_name': 'EmployeeMaster'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'allow_concurent_login': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'base_service_centre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'emp_base_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authentication.Department']"}),
            'ebs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ebs_customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'effective_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'employee_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'login_active': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'mobile_no': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'query_limit': ('django.db.models.fields.IntegerField', [], {'default': '50', 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'service_centre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']", 'null': 'True', 'blank': 'True'}),
            'staff_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '2'}),
            'temp_days': ('django.db.models.fields.IntegerField', [], {'default': '7', 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'temp_emp_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'Staff'", 'max_length': '15', 'blank': 'True'})
        },
        'billing.billing': {
            'Meta': {'object_name': 'Billing'},
            'adjustment': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'adjustment_cr': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'bill_generation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cess_higher_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_applied_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_subtract_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'demarrage_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'demarrage_shipments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'billing_demarrage_shipments'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"}),
            'education_secondary_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'generation_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'received': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'service_tax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment_count': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'ship_bills'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_charge_pretax': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_payable_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'billing.billingsubcustomer': {
            'Meta': {'object_name': 'BillingSubCustomer'},
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['billing.Billing']", 'null': 'True', 'blank': 'True'}),
            'billing_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'billing_date_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cod_applied_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_subtract_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'demarrage_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'demarrage_shipments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'billingsubcustomer_demarrage_shipments'", 'symmetrical': 'False', 'to': "orm['service_centre.Shipment']"}),
            'freight_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'generation_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'reverse_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rto_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdd_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipment_count': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'shipments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['service_centre.Shipment']", 'symmetrical': 'False'}),
            'subcustomer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']"}),
            'to_pay_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total_cod_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'valuable_cargo_handling_charge': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'customer.customer': {
            'Meta': {'object_name': 'Customer'},
            'activation_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'activation_by'", 'null': 'True', 'to': "orm['auth.User']"}),
            'activation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'activation_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Address2']", 'null': 'True', 'blank': 'True'}),
            'approved': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'approver'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'authorized': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'authorizer'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'bill_delivery_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bill_delivery_hand': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'billing_schedule': ('django.db.models.fields.IntegerField', [], {'default': '7', 'max_length': '3'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'contact_person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Contact']", 'null': 'True', 'blank': 'True'}),
            'contract_from': ('django.db.models.fields.DateField', [], {}),
            'contract_to': ('django.db.models.fields.DateField', [], {}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_by'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit_limit': ('django.db.models.fields.IntegerField', [], {'default': '10000', 'max_length': '10'}),
            'credit_period': ('django.db.models.fields.IntegerField', [], {'default': '10', 'max_length': '3'}),
            'day_of_billing': ('django.db.models.fields.SmallIntegerField', [], {'default': '7'}),
            'decision_maker': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'decision_maker'", 'null': 'True', 'to': "orm['location.Contact']"}),
            'demarrage_min_amt': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'demarrage_perkg_amt': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'flat_cod_amt': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'fuel_surcharge_applicable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'legality': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Legality']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'next_bill_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'pan_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'referred_by': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'remittance_cycle': ('django.db.models.fields.SmallIntegerField', [], {'default': '7'}),
            'return_to_origin': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'reverse_charges': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'saleslead': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'saleslead'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'signed': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'signatory'", 'null': 'True', 'to': "orm['authentication.EmployeeMaster']"}),
            'tan_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'to_pay_charge': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'updated_by'", 'null': 'True', 'to': "orm['auth.User']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'vchc_min': ('django.db.models.fields.DecimalField', [], {'default': '0.5', 'max_digits': '6', 'decimal_places': '2'}),
            'vchc_min_amnt_applied': ('django.db.models.fields.IntegerField', [], {'default': '5000', 'max_length': '5'}),
            'vchc_rate': ('django.db.models.fields.DecimalField', [], {'default': '0.5', 'max_digits': '4', 'decimal_places': '2'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zone_label': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['location.ZoneLabel']", 'null': 'True', 'blank': 'True'})
        },
        'customer.shipper': {
            'Meta': {'object_name': 'Shipper'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Address']", 'null': 'True', 'blank': 'True'}),
            'alias_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'ecomm_admin.legality': {
            'Meta': {'object_name': 'Legality'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legality_type': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'ecomm_admin.mode': {
            'Meta': {'object_name': 'Mode'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'ecomm_admin.shipmentstatusmaster': {
            'Meta': {'ordering': "['code']", 'object_name': 'ShipmentStatusMaster'},
            'code': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'code_description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'code_redirect': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'location.address': {
            'Meta': {'object_name': 'Address'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.State']"})
        },
        'location.address2': {
            'Meta': {'object_name': 'Address2'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        },
        'location.areamaster': {
            'Meta': {'object_name': 'AreaMaster'},
            'area_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'area_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'branch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Branch']"}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'location.branch': {
            'Meta': {'object_name': 'Branch'},
            'branch_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'branch_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'branch_type': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '13'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'location.city': {
            'Meta': {'object_name': 'City'},
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'city_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labeled_zones': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'label_city'", 'symmetrical': 'False', 'to': "orm['location.Zone']"}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Region']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.State']"}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Zone']"})
        },
        'location.contact': {
            'Meta': {'object_name': 'Contact'},
            'address1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'address3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'address4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']", 'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'default': "'0000-00-00'", 'null': 'True', 'blank': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.State']", 'null': 'True', 'blank': 'True'})
        },
        'location.region': {
            'Meta': {'object_name': 'Region'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'region_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'location.servicecenter': {
            'Meta': {'ordering': "['center_shortcode']", 'object_name': 'ServiceCenter'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.Address']"}),
            'center_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'center_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.City']"}),
            'contact': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['location.Contact']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processing_center': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'})
        },
        'location.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'state_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'location.zone': {
            'Meta': {'object_name': 'Zone'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ZoneLabel']", 'null': 'True', 'blank': 'True'}),
            'location_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'max_length': '1'}),
            'zone_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'zone_shortcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'location.zonelabel': {
            'Meta': {'object_name': 'ZoneLabel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'pickup.pickupregistration': {
            'Meta': {'object_name': 'PickupRegistration'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'address_line3': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'address_line4': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.AreaMaster']", 'null': 'True', 'blank': 'True'}),
            'caller_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'callers_number': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'customer_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']"}),
            'customer_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.Mode']", 'null': 'True', 'blank': 'True'}),
            'office_close_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'pickup_date': ('django.db.models.fields.DateField', [], {}),
            'pickup_route': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'pickup_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'pieces': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'product_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'regular_pickup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'reminder': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'return_subcustomer_code': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'return_subcustomer_code'", 'null': 'True', 'to': "orm['customer.Shipper']"}),
            'reverse_pickup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'service_centre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['location.ServiceCenter']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'subcustomer_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Shipper']", 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'to_pay': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'volume_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'service_centre.shipment': {
            'Meta': {'object_name': 'Shipment'},
            'actual_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {}),
            'billing': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'billing_ships'", 'null': 'True', 'to': "orm['billing.Billing']"}),
            'breadth': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'chargeable_weight': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'collectable_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'consignee': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'consignee_address1': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'consignee_address2': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'consignee_address3': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'consignee_address4': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'current_sc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'declared_value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'destination_city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'expected_dod': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscan_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'item_description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'manifest_location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manifest_location'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'mobile': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'original_dest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipment_origin_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'pickup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipment_pickup'", 'null': 'True', 'to': "orm['pickup.PickupRegistration']"}),
            'pieces': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pincode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'rd_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reason_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ecomm_admin.ShipmentStatusMaster']", 'null': 'True', 'blank': 'True'}),
            'ref_airwaybill_number': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rejection': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'return_shipment': ('django.db.models.fields.SmallIntegerField', [], {'default': 'False'}),
            'reverse_pickup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rto_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rts_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rts_reason': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rts_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sbilling': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subbilling_ships'", 'null': 'True', 'to': "orm['billing.BillingSubCustomer']"}),
            'sdd': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sdl': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'service_centre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'shipment_sc'", 'null': 'True', 'to': "orm['location.ServiceCenter']"}),
            'shipment_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'shipper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customer.Customer']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'status_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'tab': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'volumetric_weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['amazon_api']