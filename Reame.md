# OC Mailer

Mailer class for auto-notification sending

## Configuration

Is a *JSON*. Format:

```
{
    "mail_domain_1": {
            "template_type": "plain",
            "template": "template_text"            
        },
    "mail_domain_2" {
            "template_type": "html",
            "template_file": "path",
            "signature_image": "path"
        }
}
```

Number of possible `"mail_domain"` keys is not limited.

Mail domain `""` is used by-default if no suitable exact mail domains found in root keys.

Parameter `"template_type"` may be one of: `"plain"` for plain-text messages or `"html"` for *HTML*-messages.

Parameter `"template"` is a template string itself. Substitute `${text}` will be replaced by message text given in caller code. Incompatible with `"template_type": "html"`. Default is `"${text}"` and it will be used if nothing specified in configuration or caller arguments.

Parameters `"template"` and `"template_file"` are incompatible with each other if used in one `"mail_domain"` section. If both given then `"template"` will be used and `"template_file"` will be ignored.

Parameter `"signature_image"` is incompatible with `"template_type": "plain"`.

Values for `"path"` in `"template_type"` and `"signature_image"` are paths to the corresponding files. Paths may be absolute or relative. Note that *relative* paths are considered as relative to configuration file itself, **not to a current directory**.

## Usage

`Mailer(smtp_client, from_address, template_type=None, template=None, signature_image=None, config_path=None)` - to instantiate mailer class.

**Parameters**:

- `smtp_client` - client instance as returned by `smtp` module comes with *Python* interpreter.
- `from_adderss` - e-mail of "sender". **Required**.
- `template_type` - type of template to use, may be `"plain"` (default) or `"html"`. Value from *JSON* configuration will be used if omitted, see `config_path` parameter below.
- `template` - string message template. Value from *JSON* configuration will be used if omitted, see `config_path` parameter below.
- `signature_image` - binary data of signature image to use in `"html"` messages. Value from *JSON* configuration will be used if omitted, see `config_path` parameter below.
- `config_path` - path to *JSON* configuration file, see format above. Will be used default comes with this package if omitted.
