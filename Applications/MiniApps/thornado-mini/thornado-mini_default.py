import reframe as rfm
import reframe.utility.sanity as sn
import hackathon as hack

@rfm.simple_test
class ThornadoMiniTest(hack.HackathonBase):
    # Where to run the binaries 'aws:c6gn' on Arm or 'aws:c5n' on Intel
    valid_systems = ['aws:c6gn', 'aws:c5n']

    # Logging Variables
    log_team_name = 'TheClangers'
    log_app_name = 'thornado-mini'
    log_test_name = 'default'

    preruns_cmds = [
        "mkdir -p ../Output",
        "wget -O EquationOfStateTable.h5 https://code.ornl.gov/m2o/thornado-tables/-/raw/master/mini-app/wl-EOS-SFHo-15-25-50-noBCK.h5",
        "wget -O OpacityTable.h5 https://code.ornl.gov/m2o/thornado-tables/-/raw/master/mini-app/wl-Op-SFHo-15-25-50-noBCK.h5",
    ]

    # Define Execution
    # Binary to run
    executable = 'DeleptonizationProblem1D_mymachine'
    # Command line options to pass
    executable_opts = ["> thornado-mini.log"]
    # Where the output is written to
    logfile = 'thornado-mini.log'
    # Store the output file (used for validation later)
    keep_files = [logfile]

    # Parameters - Compilers - Defined as their Spack specs (use spec or hash)
    spec = parameter([
        'thornado-mini@1.0 %gcc@10.3.0',     # Thornado with the gcc compiler
        'thornado-mini@1.0 %arm@21.0.0.879', # Thornado with the Arm compiler
    ])

    # Parameters - MPI / Threads - Used for scaling studies
    parallelism = parameter([
        { 'nodes' : 1, 'mpi' : 16, 'omp' : 1},
        { 'nodes' : 1, 'mpi' : 32, 'omp' : 1},
        { 'nodes' : 1, 'mpi' : 64, 'omp' : 1},
    ])


    # TODO: this needs totally overhauling to match thornado's output
    # Code validation
    @run_before('sanity')
    def set_sanity_patterns(self):

       global_electron_regex = r'Global Electron Number =\s+(\S+)'
       # Get the final electron number
       electron_number = sn.extractall(global_electron_regex, self.logfile, 1, float)[-1]
       # expected ~3.8765834888E+057, given on first run
       expected_lower = 0.30745
       expected_lower = 3.8765825 * (10 ^ 57)
       expected_upper = 3.8765835 * (10 ^ 57)

       # Perform a bounded assert
       self.sanity_patterns = sn.assert_bounded(electron_number, expected_lower, expected_upper)

       # Performance Testing - FOM Total Time units 's'
       # We dont set an expected value
       self.reference = {
          '*': {'Total Time': (0, None, None, 's'),}
       }

       # CloverLeaf prints the 'Wall clock' every timestep - so extract all lines matching the regex
       pref_regex = r'[^d]t = ([0-9]+\.[0-9]+E[+-][0-9]+) ms'
       self.perf_patterns = {
               'Total Time': sn.extractsingle(pref_regex, self.logfile, 1, float, item=-1)
       }

