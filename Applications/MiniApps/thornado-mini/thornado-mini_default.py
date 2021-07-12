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

    # Define Execution
    # Binary to run
    executable = 'bin/DeleptonizationProblem1D_mymachine'
    # Command line options to pass
    executable_opts = []
    # Where the output is written to
    logfile = 'thornado.out'
    # Store the output file (used for validation later)
    keep_files = [logfile]

    # Parameters - Compilers - Defined as their Spack specs (use spec or hash)
    spec = parameter([
        'thornado-mini@1.0 %gcc@10.3.0',     # Thornado with the gcc compiler
        'thornado-mini@1.0 %arm', # Thornado with the Arm compiler
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

       # Use the logfile for validation testing and performance

       # Validation at step 87 (BM_short)
       # Regex - Volume   Mass   Density   Pressure   Internal Energy   Kinetic Energy   Total Energy
       sol_regex = r'\s+step:\s+87\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'
       # Validate for kinetic energy (6)
       kinetic_energy = sn.extractsingle(sol_regex, self.logfile, 6, float)

       # expected = 0.3075
       expected_lower = 0.30745
       expected_upper = 0.30755

       # Perform a bounded assert
       self.sanity_patterns = sn.assert_bounded(kinetic_energy, expected_lower, expected_upper)

       # Performance Testing - FOM Total Time units 's'
       # We dont set an expected value
       self.reference = {
          '*': {'Total Time': (0, None, None, 's'),}
       }

       # CloverLeaf prints the 'Wall clock' every timestep - so extract all lines matching the regex
       pref_regex = r'\s+Wall clock\s+(\S+)'
       self.perf_patterns = {
               'Total Time': sn.extractsingle(pref_regex, self.logfile, 1, float, item=-1)
       }

