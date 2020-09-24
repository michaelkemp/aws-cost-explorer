# aws-cost-explorer

## Install AWS Command Line Tool and BYU's AWSlogin on Ubuntu

- Add pip3 and unzip
    - ```sudo apt install unzip```
    - ```sudo apt install python3-pip```
- Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html)
    - ```curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"```
    - ```unzip awscliv2.zip```
    - ```sudo ./aws/install```
    - ```aws --version```
- Install [BYU's awslogin](https://github.com/byu-oit/awslogin)
    - ```pip3 install --upgrade byu_awslogin```
- Add $HOME/.local/bin to path
    - ```
        vim .bashrc
            if [ -d "$HOME/.local/bin" ] ; then
                PATH="$HOME/.local/bin:$PATH"
            fi
        source .bashrc


## Login to ONE AWS Account via the Command Line

- Clean up old credentials if needed
    - ```rm ~/.aws/config```
    - ```rm ~/.aws/credentials```
- Log in to single account [It will request your netid/password and MFA]
    - ```awslogin --account byu-org-trn --role PowerUser```
- Run the Cost Explorer Script
    - ```python3 cost-explorer.py```

## Login to MANY AWS Account via the Command Line

- Clean up old credentials if needed
    - ```rm ~/.aws/config```
    - ```rm ~/.aws/credentials```
- Log in to single account [It will request your netid/password and MFA]
    - ```awslogin --account all --role PowerUser```
- Run the Cost Explorer Script for ALL logged in accounts
    - ```python3 cost-explorer.py```
- Run the Cost Explorer Script for a single logged in account
    - ```python3 cost-explorer.py byu-org-trn```


