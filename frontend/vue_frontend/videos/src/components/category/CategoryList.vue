<template>
    <div>
        <table id="category-list-table" class="table table-striped table-bordered">
        <thead>
            <tr>
                <th width="7%">Ativo</th>
                <th>Nome da Categoria</th>
                <th width="20%" class="text-center hidden-xs"># Vídeos</th>
                <th width="5%"></th>
            </tr>
        </thead>
        <tbody>
            <category-list-item v-for="item in items" :key="item.pk" :item="item"  />
        </tbody>
        </table>
    </div>
</template>

<script>
    import CategoryListItem from "./CategoryListItem";

    export default {
        name: 'CategoryList',
        components: {CategoryListItem},
        props: {
            items: {
                type: Array,
                required: true
            }
        },
        data() {
            return {
                'datatable': null
            }
        },
        mounted() {
            this.$category_store.commit('addHook', {
                'type': 'after',
                'id': 'category.list.reload',
                'callback': () => this.reload()
            });
            this.configureDatatables();
        },
        methods: {
            setupSwitches() {
                window.setTimeout(() => window.app.switcheryToggle(), 300);
            },
            configureDatatables() {
                window.setTimeout(() => {

                    this.datatable = window.$('#category-list-table').DataTable({
                        "language": {
                            sEmptyTable: "Nenhum registro encontrado",
                            sInfo: "Mostrando de _START_ até _END_ de _TOTAL_ registros",
                            sInfoEmpty: "Mostrando 0 até 0 de 0 registros",
                            sInfoFiltered: "(Filtrados de _MAX_ registros)",
                            sInfoPostFix: "",
                            sInfoThousands: ".",
                            sLengthMenu: "_MENU_ resultados por página",
                            sLoadingRecords: "Carregando...",
                            sProcessing: "Processando...",
                            sZeroRecords: "Nenhum registro encontrado",
                            sSearch: "Pesquisar",
                            oPaginate: {
                                sNext: "Próximo",
                                sPrevious: "Anterior",
                                sFirst: "Primeiro",
                                sLast: "Último"
                            },
                            oAria: {
                                sSortAscending: ": Ordenar colunas de forma ascendente",
                                sSortDescending: ": Ordenar colunas de forma descendente"
                            }
                        },
                        "columnDefs": [
                            // Disable sort in first, last column
                            {
                                "searchable": false,
                                "orderable": false,
                                "className": "text-center",
                                "targets": -1
                            },
                            {
                                "searchable": false,
                                "orderable": false,
                                "className": "nowrap",
                                "targets": 0
                            }
                        ],
                        // Default order
                        "order": [[1, 'asc']]
                    });

                    this.setupSwitches();

                }, 300);
            },
            reload() {
                if (!this.datatable) {
                    this.setupSwitches();
                    return;
                }
                this.datatable.destroy();
                this.configureDatatables();
            }
        }
    }
</script>