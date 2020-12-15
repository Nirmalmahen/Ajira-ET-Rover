class Inventory:
    maxSize=10
    size=0
    inventoryItemsSampleList=dict()

class InventoryItem:
    sampleName=""
    samplePriority=0
    sampleSize=0

def addItem(InventoryItem,Inventory):
    while(InventoryItem.sampleSize+ Inventory.size>Inventory.maxSize):
        leastKey=min(Inventory.inventoryItemsSampleList, key=int)
        if (Inventory.inventoryItemsSampleList[leastKey]==1):
            Inventory.size-=Inventory.inventoryItemsSampleList[leastKey].size
            del Inventory.inventoryItemsSampleList[leastKey]

        else:
            Inventory.size -= Inventory.inventoryItemsSampleList[leastKey].size
            Inventory.inventoryItemsSampleList[leastKey]-=1
    if InventoryItem.samplePriority in Inventory.inventoryItemsSampleList:
        Inventory.inventoryItemsSampleList[InventoryItem.samplePriority] += 1
        Inventory.size += Inventory.inventoryItemsSampleList[InventoryItem.samplePriority].size
    else:
        Inventory.size += Inventory.inventoryItemsSampleList[InventoryItem.samplePriority].size
        Inventory.inventoryItemsSampleList[InventoryItem.samplePriority]=1


















