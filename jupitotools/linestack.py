"""Line stacks."""

# #### OLD
# stacky push  # Push lines from stdin to stack
# stacky push LINE  # Push LINE to stack
# stacky pushn ITEM1 ITEM2 ...  # Push multiple items
# stacky pop  # Pop line from stack
# stacky pop N # Pop N lines from stack
# stacky peek  # Output line without popping
# ~/.local/share/stacky/stack  # Default stack file
# ~/.config/stacky/stacky.cfg  # Config file, use format "--param foobar"
# ####

from pathlib import Path


class LineStack:
    """..."""

    def __init__(self, path):
        """..."""
        self.path = Path(path)
        self.bak_path = path.with_suffix(path.suffix + '.bak')
        self.popped_path = path.with_suffix(path.suffix + '.popped')

    def nlines(self):
        """..."""
        with self.path.open() as read:
            return sum(1 for _ in read)

    def pop(self):
        """..."""
        self.path.replace(self.bak_path)  # TODO: Copy instead of moving.
        with self.bak_path.open() as read, self.path.open('w') as write:
            line = read.readline()
            self.popped_path.write_text(line)
            write.writelines(read)
        return line
