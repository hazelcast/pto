PTO Stands for Performance Test Orchestrator 



# Ramblings

My task right now is to automate the installation of ITCH, which is a simple java 
program.  The parts are, a JVM, a config file with all private IPs and the java 
program itself, packaged as a jar.  

Should I upload it ? or download it from git and build it ?

Should I use the JVM installer from hazelcast-simulator ? 

Should the script start it as well ?

How will I get the IPs ?

In which project should I put this code ? The options appear to be hazelcast-simulator, PTO 
or application-benchmarks.

To add to the complication, each benchmark will be heavily modified with its own scripts
and configuration files.  The model used by hazelcast-simulator is good.  It creates a new benchmark 
directory which contains all the tools you need for running a benchmark.  The main thing I don't like about 
adding this to hazelcast-simulator is that I want more control over provisioning, which would mean 
updating the Terraform template, which I don't want to do.

I like the idea of having an independent orchestrator so I don't have to make extensive modifications
to hazelcast-simulator.

Heres a plan ...

Copy stuff from application-benchmarks into PTO to provision the environment.  
Create a "test" using Hazelcast simultator.  Using orchestration, copy the 
inventory emulator into the correct location within the new simulator test.
Use PTO to call install java and install simulator on the test environment.
Write an ansible script that assumes java is installed.  The script will need to 
check for java, install maven, clone and build itch, generate the config file and 
stsart itch.  I will need to update my "setup" script to put local addresses in the 
inventory file.
