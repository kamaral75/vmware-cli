"""Module containing classes for working with VMWare API."""

from __future__ import print_function

import argparse
import atexit
import base64
import getpass
import ssl

from datetime import datetime
from config import *

from pyVim import connect
from pyVmomi import vim
from pyVmomi import vmodl

class VMWare(object):
    """Class for working with the VMWare API."""

    def __init__(self, username, password, url, port, verbose=False):
        """Initatator method."""
        self.username = username
        self.password = password
        self.url = url
        self.port = port
        self.verbose = verbose

    def connect_vsphere(self):
        service_instance = None
        ssl_verification = False

        try:
            if ssl_verification:
                service_instance = connect.SmartConnect(host=self.url,
                                                            user=self.username,
                                                            pwd=self.password,
                                                            port=int(self.port))

            else:
                service_instance = connect.SmartConnectNoSSL(host=self.url,
                                                            user=self.username,
                                                            pwd=self.password,
                                                            port=int(self.port))

            # Disconnect session
            atexit.register(connect.Disconnect, service_instance)
            return service_instance

        except Exception as e:
            print('ERROR: Unable to connect to vCenter server. ', e)
            raise SystemExit("\nUnable to connect to vCenter server.\n", e)

    def get_vm_inventory(self, service_instance):
        """
        Get a full inventory of virtual machine objects from the VMWare API
        Args:
          service_instance (obj): A service instance object that has been authenticated with the VMWare API
        """

        try:
            content = service_instance.RetrieveContent()
            # Root folder
            container = content.rootFolder
            # Objects to search
            viewType = [vim.VirtualMachine]
            recursive = True
            containerView = content.viewManager.CreateContainerView(
                container, viewType, recursive)

            virtual_machines = containerView.view
            return virtual_machines

        except Exception as e:
            print('ERROR: Unable to get Virtual Machine inventory. ', e)
            raise SystemExit("\nUnable to get Virtual Machine inventory.\n", e)

    def parse_vm_inventory(self, virtual_machines):
        """
        Take the full inventory of virtual machine objects from the VMWare API and parse into individual objects
        Convert each object to a python dictionary
        Return a list of dictionaries, one for each virtual machine object
        Args:
          service_instance (obj): A full list of virtual_machines
        """

        # Initialize an empty list to store each virtual machine dictionary
        parsed_vms = []

        # Iterate full inventory of virtual machine objects
        # Create a dictionary for each virtual machine with an embedded list of network adapters
        for virtual_machine in virtual_machines:
            # Get parsed vm summary and store in a dictionary
            parsed_vm_summary = self.parse_vm_summary(virtual_machine)

            # Get parsed vm network adapters and store in a list
            parsed_vm_nics = self.parse_vm_nics(virtual_machine)

            # Embed the parsed network adapters list into the parsed vm summary dictionary
            parsed_vm_summary['Network Adapters'] = parsed_vm_nics

            # Append parsed vm summary dictionary to parsed vm list
            parsed_vms.append(parsed_vm_summary)

        return parsed_vms

    def parse_vm_summary(self, virtual_machine):
        """
        Parse virtual machine object and convert to python dictionary for a particular virtual machine
        or recurse into a folder with depth protection
        Args:
          virtual_machine (obj): A single virtual machine object returned from the VMWare API
        """

        # Initialize empty dictionary to store properties of a single virtual machine object
        row = {}

        summary = virtual_machine.summary
        row['Name'] = summary.config.name
        row['Template'] = summary.config.template
        row['Path'] = summary.config.vmPathName
        row['Guest'] = summary.config.guestFullName
        row['Instance UUID'] = summary.config.instanceUuid
        row['Bios UUID'] = summary.config.uuid

        annotation = summary.config.annotation
        if annotation:
            row['Annotation'] = annotation
        else:
            row['Annotation'] = 'None'

        row['State'] = summary.runtime.powerState

        if summary.guest is not None:
            ip_address = summary.guest.ipAddress
            tools_version = summary.guest.toolsStatus
            if ip_address:
                row['Guest IP Address'] = ip_address
            else:
                row['Guest IP Address'] = 'None'
            if tools_version is not None:
                row['VMware-tools'] = tools_version
            else:
                row['VMware-tools'] = 'None'
        if summary.runtime.question is not None:
            row['Runtime Question'] = summary.runtime.question.text
        product = summary.config.product
        if product is not None:
            row['Product Name'] = product.name
            row['Vendor'] = product.vendor

        return row

    def parse_vm_nics(self, virtual_machine):
        """
        Parse a virtual machine object, get all network adatpers and convert to a dictionary
        Return a list of dictionaries
        Args:
          virtual_machine (obj): A single virtual machine object returned from the VMWare API
        """

        # Initialize empty list to store one or more dictionaries for each network adapter
        network_adapters = []

        for dev in virtual_machine.config.hardware.device:
            if isinstance(dev, vim.vm.device.VirtualVmxnet3) or isinstance(dev, vim.vm.device.VirtualEthernetCard):
                # Initialize empty dictionary to store properties of a single network adapter
                nic = {}
                nic['Mac Address'] = dev.macAddress
                nic['Label'] = dev.deviceInfo.label
                # Add network adapter to network adapters list
                network_adapters.append(nic)

        return network_adapters

    def get_parsed_inventory(self):
        """Get inventory of all VMWare instances."""

        service_instance = None
        virtual_machines = None

        service_instance = self.connect_vsphere()

        if service_instance is not None:
            virtual_machines = self.get_vm_inventory(service_instance)

        if virtual_machines is not None:
            parsed_vms = self.parse_vm_inventory(virtual_machines)

        if parsed_vms:
            return parsed_vms

        else:
            return False


def main():
  # Initialize VMWareAPI class
  vmwareAPI = VMWareAPI(vmware_username, vmware_password, vmware_hostname, vmware_port)
  # Call get_vm_inventory
  vmwareAPI.get_vm_inventory()

if __name__ == "__main__":
  main()