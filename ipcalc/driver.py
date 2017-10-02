from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import InitCommandContext, ResourceCommandContext
import cloudshell.api.cloudshell_api as api
from natsort import natsorted, ns
import ipcalc
import json

class IpcalcDriver (ResourceDriverInterface):
    # Calc sizes for common subnets
    NetSizes = {}
    NetSizes["24"] = 254 + 2
    NetSizes["25"] = 126 + 2
    NetSizes["26"] = 62 + 2
    NetSizes["27"] = 30 + 2
    NetSizes["28"] = 14 + 2
    NetSizes["29"] = 6 + 2
    NetSizes["30"] = 2 + 2
    NetSizes["31"] = 2

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def printIPsInContainer(self, context, containerName):
        ApiSession = api.CloudShellAPISession(host=context.connectivity.server_address, token_id=context.connectivity.admin_auth_token, domain="Global")

        try:
            containerResource = ApiSession.GetResourceDetails(containerName)
        except:
            raise ValueError("Specified container does not exist.")

        rl = ApiSession.FindResources(resourceFamily="Address",resourceModel="IP Address", includeSubResources=True)
        cleanList = []

        for address in rl.Resources:
            if (containerName in address.FullName):
                cleanList.append(address.Name)


        cleanList = natsorted(cleanList, alg=ns.IGNORECASE)
        return json.dumps(cleanList)



    def getNextIP(self, context, containerName, CIDR):
        ApiSession = api.CloudShellAPISession(host=context.connectivity.server_address, token_id=context.connectivity.admin_auth_token, domain="Global")

        # validate that the container to pull from exists in RM in this domain
        try:
            containerResource = ApiSession.GetResourceDetails(containerName)
        except:
            raise ValueError("Specified container does not exist.")

        rl = ApiSession.FindResources(resourceFamily="Address",resourceModel="IP Address", includeSubResources=True)
        cleanList = []

        for address in rl.Resources:
            if (containerName in address.FullName):
                if ((address.ReservedStatus == "Not In Reservations") and (address.Excluded == False)):
                    cleanList.append(address.Name)

        cleanList = natsorted(cleanList, alg=ns.IGNORECASE)

        # we now have a sorted list of IPs which are available
        # that are in the given container (cleanList). It is
        # sorted to be in numeric order. We also have the
        # original list of resource objects still (rl)

        containerCidr = str(containerResource.ResourceAttributes[0].Value)

        # Confirm that the requested size is possible given the allocated range we are managing
        if(int(CIDR)<int(containerCidr)):
            raise ValueError("Requested network size is greater than allocated container has to offer.")

        try:
            numAddressesNeeded = self.NetSizes[CIDR]
        except:
            raise ValueError("The subnet size requested cannot be converted into available IP space.")

        # confirm that we still have enough addresses to handle the requested subnet size
        if(numAddressesNeeded > len(cleanList)):
            raise ValueError("The requested number of IPs needed for this sandbox do not exist in this allocation range of " + containerName)

        # I guess we are ok now so handle this request
        i = 0
        returnedAddresses = []
        try:
            while (i < numAddressesNeeded):
                newIP = containerName + "/" + cleanList[i]
                returnedAddresses.append(newIP)
                i = i + 1
            ApiSession.AddResourcesToReservation(reservationId=context.reservation.reservation_id,resourcesFullPath=returnedAddresses)
        except:
            raise ValueError("Something went wrong allocating the IPs.")

        return json.dumps(returnedAddresses)