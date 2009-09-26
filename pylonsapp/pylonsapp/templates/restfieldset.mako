<html><body>

<div>
  %if is_grid:
    <h3>${getattr(fs, '__name__', fs.model.__class__.__name__)} listing</h3>
    <div class="pager">
      ${page.pager()|n}
    </div>
    <table>
      ${fs.render()|n}
    </table>
  %else:
    %if action:
      %if id:
        <h3>Edit ${getattr(fs, '__name__', fs.model.__class__.__name__)}</h3>
        <form action="${action}" method="POST">
          ${fs.render()|n}
          <input type="hidden" name="_method" value="PUT" />
          <input type="submit" />
        </form>
      %else:
        <h3>Add ${getattr(fs, '__name__', fs.model.__class__.__name__)}</h3>
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

</body></html>
