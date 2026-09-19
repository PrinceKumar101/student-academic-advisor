import { EmptyState } from "./EmptyState";

type SimpleTableProps = {
  columns: string[];
  rows: Array<Array<string | number | null>>;
  caption: string;
  empty?: string;
};

export function SimpleTable({ columns, rows, caption, empty = "No rows" }: SimpleTableProps) {
  if (rows.length === 0) {
    return <EmptyState title={empty} />;
  }
  return (
    <div className="max-w-full overflow-x-auto">
      <table className="saa-table min-w-[36rem]">
        <caption>{caption}</caption>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column} scope="col">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index} className="saa-enter">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex}>{cell ?? "—"}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
