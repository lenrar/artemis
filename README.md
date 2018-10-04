# artemis <img src="artemis.png"  width="10%" height="10%">

## description
artemis is a pet food optimizer tool. given a budget, pet type, and pet food consumption it will output the highest quality food for your pet.

highest quality in this case means max protein, minimal carbs, and fat as close to 20% as possible. this isn't meant to be used very seriously.
## setup
to run, clone and then create a new anaconda environment with
`conda env create -f environment.yml`
then, activate the environment with

windows:
`activate artemis-env`
mac/linux:
`source activate`

finally, run
`python artemis.py`
to kick off the tool
