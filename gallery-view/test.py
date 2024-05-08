import re

url = "https://finalsohaibstorage.file.core.windows.net/phovinoshare/username/d70df772-2828-42ea-889a-7259e6f34986.jpg?sv=2022-11-02&ss=bfqt&srt=o&sp=rwdlacupiytfx&se=2023-12-18T21:02:41Z&st=2023-12-18T13:02:41Z&spr=https&sig=1xXznplvyhBaod7AFS0fRaCiTiraY7+hrq6c00au0H8="

# New SAS token
new_sas_token = "your_new_sas_token"

# Use regular expression to replace the content after .jpg
modified_url = re.sub(r'(?<=\.jp).*$', 'g' + new_sas_token, url)

print(modified_url)
