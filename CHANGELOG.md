# Changelog

## Alpha-version 1.0.2b
**01-11-2020**
*Released 1.0.2b*

* Cloud and folder methods:
  * Cloud as object
  * Folder as object
  * List of operations
  * Method for create folder
* Fixed minor issues
* Added configs for development
* Fixed docs


## Alpha-version 1.0.1
**31-10-2020**
*Released 1.0.1*

* Certificate Manager Client added and support methods:
  * Create Let's Encrypt free certificate
  * Get certificate (also with fullchain and private key)
  * Delete certificate
  * Show certificate operations
* Fixed minor issues


## Alpha-version 1.0

**01-04-2020**
*Released 1.0*

* Base Client provides an interface for working with:
  * Authorization with the use:
    * OAuth-token
    * IAM-token
    * service account key
  * Endpoints
  * Operations

  * In the future:
    * Clouds  # placebo now
    * Folders  # placebo now
    * Access Bindings  # placebo now
    * IAM (users, service accounts, tokens, keys, etc)  # plplacebo nowacebo

* Client for Compute Cloud Service provides an interface for working with:
  * Instances
  * Disks
  * Snapshots
  * Images
