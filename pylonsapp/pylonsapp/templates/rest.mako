<html>
    <head>
    </head>
    <body>
        <div>
          %if is_grid:
            <table>
              ${fs.render()|n}
            </table>
          %else:
            %if action:
              %if id:
                <h3>Edit</h3>
                <form action="${action}" method="POST">
                  ${fs.render()|n}
                  <input type="hidden" name="_method" value="PUT" />
                  <input type="submit" />
                </form>
              %else:
                <h3>Add</h3>
                <form action="${action}" method="POST">
                  ${fs.render()|n}
                  <input type="submit" />
                </form>
              %endif
            %else:
              <table>
                ${fs.render()|n}
              </table>
            %endif
          %endif
        </div>
    </body>
</html>
