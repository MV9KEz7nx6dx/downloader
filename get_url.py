
import lk21
import sys


def sbembed(link: str) -> str:
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_sbembed(link)
    lst_link = []
    count = len(dl_url)
    for i in dl_url:
        lst_link.append(dl_url[i])
    return lst_link[count - 1]


link = sbembed(sys.argv[1])
print(link)
