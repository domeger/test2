# Container Template for use with BeeKeeper Enclaves

Welcome to the BeeKeeper encryption tutorial. In this tutorial you will take an example application that works in BeeKeeper and you will be able to encrypt and run all of the components of this example. After you've got a good handle on how the system is designed, you can replace the example application with your own application. As you hook into the example with your applcation, you should seek assistance from the team at BeeKeeper to guide you if you run into problems.

# Step 0: Understanding The Process

## What is this example?

This application is a container that presents a very simple flask-based POSTable endpoint for which an x-ray image can be interpretted for the presenence of pneumonia, COVID-19, or the absence of both diseases. In this repository, you will find the following files which you can adapt to your application:

1. An example [Dockerfile](Dockerfile) (this has the logic required for BeeKeeper to decrypt your secrets at _runtime_)
2. An example [app.py](app.py) (this is the simple Flask application)
3. An example secret ([multi-class-pg.pkl](models/multi-class-pg.pkl)) model
4. A critically important [entrypoint.sh](bkopen/entrypoint.sh) which you must modify to have your runtime _after_ BeeKeeper decryption steps
5. An example secrets manifest [secrets.yaml](secrets.yaml) which instructs BeeKeeper to decrypt certain files prior to running your application as defined in [entrypoint.sh](bkopen/entrypoint.sh)
6. A pythonic utility [encrypt.py](bkopen/encrypt.py) to automatically encrypt all of the files you defined in #6 above.
7. And an example public key [ao.pub.pem](ao.pub.pem). You will **always** get this from BeeKeeperAI and if you have not replaced this file during the build process, the application will fail.

# How can I test the sample application?

You can find sample images of COVID/Pneumonia at a number of different sources including https://github.com/ieee8023/covid-chestxray-dataset. When this application is run, you simply need to ensure you access the application at http://localhost:5000/apidocs/ where you will find swagger documentation that can be used to upload a sample image and have the model inference run against your data. 

## How does this all work?

The Dockerfile included here relies on you 1) adding pre-encrypted secrets (i.e., your payload) as defined in the steps ahead and 2) ensuring your entrypoint is defined in `entrypoint.sh` after the existing decryption step. You will build this container and you should expect it to fail to run given that the payload of secrets is encrypted. At runtime, the authorized enclave will decrypt your secrets and execution should proceed as expected.

## What prerequisites do I need to be successful?

### Docker Knowledge

This template assumes an understanding of the Docker container build system. If you're new to Docker or need a refresher, the Docker documentation is quite strong and the first half of the [getting-started tutorial](https://docs.docker.com/get-started/) on Docker.com can be very helpful.

### Technial Prerequisites

You will need the following items installed on your development machine to execute these steps

- Python3
- Docker Version 20+
- Bash

### Your Code Requirements

This templated example is meant for you to replace the example application with your application. You will want to review the comments in `Dockerfile`, `secrets.yaml`, and `bkopen/entrypoint.sh` to understand how the BeeKeeper decryption and encryption pathways are built.

In order for your application to be driven by BeeKeeper with data from a data steward, you need to expose an endpoint where data can be POSTed to your service and a corresponding result can be returned. These results will be accumulated and reported in aggregate by BeeKeeper.

# Step 1: Obtain Your Enclave Public Key

BeeKeeperAI Enclaves generate public keys for you to encrypt your secrets. This public key you'll receive will be in a PEM format and will be obtained from either beekeeperai.com or can be obtained from your customer success engineer at BeeKeeperAI. You can validate your pem file (typically `ao.pub.pem`) by running the following at your command prompt:

```Bash
openssl pkey -inform PEM -pubin -in ao.pub.pem -pubcheck -noout
# Key is valid
```

If you discover you are not seeing `Key is valid` from the check above, stop and check with BeeKeeperAI for support.

# Step 2: Creating Your Manifest and Encrypting Your Files

BeeKeeper decodes YAML to understand the locations of your secret files for decryption at runtime. We will therefore need to create a manifest file that is correctly formatted. This repository contains [secrets.yaml](secrets.yaml) which you can use to help guide your own secrets.yaml creation. Before we start encrypting, you should read the secrets.yaml comments to understand how it is created:

```Yaml
# Each item in the manifest maps an encrypted source file to an unencrypted destination file
# All paths should reflect the container's layout and not the layout as created in Docker
secretFiles:
 - ["models/multi-class-pg.pkl.bkenc", "models/multi-class-pg.pkl"]
```

After you have created your `secrets.yaml` file with the appropriate set of secret files, you can then proceed to encrypt all of your files.

```Bash
# With your secrets yaml file created, a BeeKeeperAI encryption utility will use your `ao.pub.pem` file to create a fully encrypted chain of trust with all of your defined secrets encrypted.

python3 bkopen/encrypt.py
```

If you discover this does not work, be sure you have the appropriate dependencies installed:

```Bash
# You may want to consider a more advanced installation by running:
# python3 -m venv .venv
# source .venv/bin/activate
# this will protect your system from these dependencies you'll install below
pip3 install cryptography pyyaml
```

# Step 3: Delete Private Files from Repo

It is incredibly critical to keep all secrets either enciphered or out of your respository. In the process of encrypting your payload, we generated the following files which must be either saved securely or deleted:

NOTE: With the exception of #3 below, all of this is typically done automatically, but you should still follow the steps below to ensure you have protected your secrets.

1. For every `.bkenc` file that you have created, ***delete*** the original file from your directory; we will decrypt the files at run time, your secrets should not be built into your docker image
2. Be sure to ***delete*** the ao.pub.pem file from your repository. While this is safe to share it is not required beyond this build process.
3. If you would like to test your image, save secret.key to a location outside of the repository. The file should be ***deleted*** from the repository and is now enciphered in the as secret.key.bkenc
4. secret.key.bkenc should ***remain*** in your respository.
5. secret.iv should ***remain*** in your repository.

In the case of this example, here is how you would clean up the repository:

```Bash
# STEP 1: Lets Remove Your Secret files (which are now encrypted as *.bkenc files)
rm models/multi-class-pg.pkl

# STEP 2: Lets remove the Model Owner Public Key
rm ao.pub.pem

# STEP 3: Lets first delete the secret.key (if you plan to test your repo, save this elsewhere)
rm secret.key

# STEP 4: Lets verify the secret.key.bkenc is still in your directory. You should see the file listed back when this is executed.
ls -lt secret.key.bkenc 

# STEP 5: Lets verify the secret.iv is still in your directory like we did above.
ls -lt secret.iv
```

# Step 4: Build your image and push it!

You have completed the hardest part of the process! Congratulations! Now, head over to beekeeperai.com and follow the upload algorith procedure and push your image!

Here are examples of commands you will receive from beekeeperai.com. Critically, these are not things to copy and paste!

```Bash
# Login to private container registry
docker login -u U53RN4M3 -p P@55w0rd bkregistry.azurecr.io

# Tag local docker build 
docker build . -t bkregistry.azurecr.io/LONG-UUID-HERE/EVEN-LONGER-UUID-HERE

# Push docker build
docker push bkregistry.azurecr.io/LONG-UUID-HERE/EVEN-LONGER-UUID-HERE
```

# Step 5: Proceed to modify the Example for your code

It is critical that you modify the dockerfile in the section designated in the center of the file. The CMD/ENTRYPOINT Dockerfile syntax should not be changed in the Dockerfile, but instead you should modify the [entrypoint.sh](/bkopen/entrypoint.sh) to include your appropriate entrypoint steps AFTER the set of steps that open and decrypt your payload.

This is where the meat of your own application's logic is going to be applied to the template. You should understand the example well before you proceed to modify the code here. Stay in touch with the team at BeeKeeper and we will help guide you through the process as you kick this off.

# Testing Your Code

If you've arrived at this section, you are touching our most advanced Algorithm Owner topic. In order to test this docker build, you will simulate the enclave by giving the secret.key to the [decrypt.py](bkopen/decrypt.py) script. This will recreate your original files.

```Bash
cp /your/secret/vault/secret.key /run/secret.key
python3 bkopen/decrypt.py
```
