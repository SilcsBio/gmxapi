import gmx
import gmx.util
from gmx import exceptions

class System(object):
    """Gromacs simulation system objects.

    A System object connects all of the objects necessary to describe a molecular
    system to be simulated.

    Once a system is created, objects can be attached or edited, accessed through
    the following properties.

    Attributes:
        workflow: element of work to be executed.

    Example:

        >>> my_sim = gmx.System._from_file(tpr_filename)
        >>> status = my_sim.run()

    Example:

        >>> my_sim = gmx.System._from_file(tpr_filename)
        >>> # Launch exectution of the runner and work on available resources.
        >>> with gmx.context.DefaultContext(system) as session:
        ...     # Run the work specified in the TPR file
        ...     session.run()
        ...     # Extend the simulation and run an additional 1000 steps.
        ...     # (version 0.1.0)
        ...     #status = session.run(1000)
        ...     print(status)
        ...
        gmx.Status(True)
        Success
        >>>

    """

    def __init__(self):
        self.__workflow = None

    @property
    def workflow(self):
        return self.__workflow

    @workflow.setter
    def workflow(self, work):
        self.__workflow = work

    @staticmethod
    def _from_file(inputrecord):
        """Process a file to create a System object.

        Calls an appropriate helper function to parse a file in the current
        context and create a System object. If no Context is currently bound, a
        local default context is created and bound.

        TODO: clarify the file location relative to the execution context.
        Until then, this helper method should not be part of the public
        interface.

        Args:
            inputrecord (str): input file name

        Returns:
            gmx.System

        Example:
            simulation = gmx.System._from_file('membrane.tpr')
            status = simulation.run()

        """
        import gmx.core
        if gmx.util._filetype(inputrecord) is gmx.fileio.TprFile:
            # we use the API to process TPR files. We create a MD module and
            # retrieve a system from its contents.
            newsystem = gmx.core.from_tpr(inputrecord)
            if newsystem is None:
                raise gmx.Error("Got empty system when reading TPR file.")
        else:
            raise gmx.UsageError("Need a TPR file.")

        system = System()
        system.workflow = newsystem

        return system

    def add_potential(self, potential):
        if (hasattr(potential, "bind")):
            self.workflow.add_potential(potential)
        else:
            raise exceptions.UsageError("Cannot add a potential that does not have a 'bind' method.")

    def run(self, parameters=None):
        """Launch execution.

        If the System is attached to a Context, the Context is initialized, if
        necessary, and its instance run()
        method is called. If there is not yet a Context, one is created and then
        used.

        Note: currently always initializes new context informed by the runner.

        Args:
            parameters: optional parameters to pass to runner. Parameter type varies by runner type.
        Returns:
            Gromacs status object.

        """
        with gmx.context.DefaultContext(self.workflow) as session:
            if parameters is None:
                return session.run()
            else:
                return session.run(parameters)