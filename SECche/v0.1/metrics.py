def findVariables():
    options = []
    for i in response_json['facts']['us-gaap']:
        options.append(i)

    for i in options:
        try:
            if "Deprecated" in response_json['facts']['us-gaap'][i]['label']:
                print("DEPRECATED - " + i)
            else:
                print(i)
        except:
            print ("ERROR - " + i)
#Call this if need to find all the variable options, some may become deprecated. 