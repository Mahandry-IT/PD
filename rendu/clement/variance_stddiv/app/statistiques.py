import ast
import json
import math
import os
from abc import ABC, abstractmethod
from pathlib import Path


class IConfiguredAbstractPopulationStatisticalOperationBean(ABC):
    @abstractmethod
    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        raise NotImplementedError


class IConfiguredAbstractPopulationVarianceBean(
    IConfiguredAbstractPopulationStatisticalOperationBean
):
    pass


class IConfiguredAbstractPopulationMeanBean(
    IConfiguredAbstractPopulationStatisticalOperationBean
):
    pass


class IConfiguredAbstractPopulationStandardDeviationBean(
    IConfiguredAbstractPopulationStatisticalOperationBean
):
    pass


class IConfiguredAbstractPopulationMeanResolutionStrategyBean(ABC):
    @abstractmethod
    def configuredResolvePopulationMean(
        self,
        configuredPopulationNumericCollection,
    ):
        raise NotImplementedError


class IConfiguredAbstractJsonNormalizationBean(ABC):
    @abstractmethod
    def configuredNormalizeJsonSerializableNumericPayload(
        self,
        configuredPayload,
    ):
        raise NotImplementedError


class DefaultConfiguredEnterpriseJsonNormalizationBeanImpl(
    IConfiguredAbstractJsonNormalizationBean
):
    def configuredNormalizeJsonSerializableNumericPayload(
        self,
        configuredPayload,
    ):
        # Oui, c'est volontairement absurde. Le but de l'exercice est d'etre chiant.
        return json.loads(
            json.dumps(
                json.loads(
                    json.dumps(
                        json.loads(json.dumps(configuredPayload))
                    )
                )
            )
        )


class DefaultConfiguredPopulationMeanResolutionStrategyBeanImpl(
    IConfiguredAbstractPopulationMeanResolutionStrategyBean
):
    def __init__(self, configuredNormalizationBean):
        self.__configuredNormalizationBean = configuredNormalizationBean

    def configuredResolvePopulationMean(
        self,
        configuredPopulationNumericCollection,
    ):
        configuredNormalizedCollection = (
            self.__configuredNormalizationBean
            .configuredNormalizeJsonSerializableNumericPayload(
                configuredPopulationNumericCollection
            )
        )

        configuredAccumulatedNumericPopulationValue = 0.0

        for configuredCurrentPopulationNumericValue in configuredNormalizedCollection:
            configuredAccumulatedNumericPopulationValue += (
                configuredCurrentPopulationNumericValue
            )

        return configuredAccumulatedNumericPopulationValue / len(
            configuredNormalizedCollection
        )


class DefaultConfiguredPopulationMeanBeanImpl(
    IConfiguredAbstractPopulationMeanBean
):
    def __init__(self, configuredMeanResolutionStrategyBean):
        self.__configuredMeanResolutionStrategyBean = (
            configuredMeanResolutionStrategyBean
        )

    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        if len(configuredPopulationNumericDataTransferObject) == 0:
            return None

        return (
            self.__configuredMeanResolutionStrategyBean
            .configuredResolvePopulationMean(
                configuredPopulationNumericDataTransferObject
            )
        )


class IlianConfiguredPopulationMeanBeanImpl(IConfiguredAbstractPopulationMeanBean):
    def __init__(self, configuredIlianPythonFile):
        self.__configuredIlianPythonFile = (
            Path(configuredIlianPythonFile).expanduser()
            if configuredIlianPythonFile
            else None
        )
        self.__configuredIlianMeanFunction = None

    def __configuredLoadIlianMeanFunction(self):
        if self.__configuredIlianPythonFile is None:
            raise RuntimeError("ILIAN_MOYENNE_FILE n'est pas configure.")

        if not self.__configuredIlianPythonFile.is_file():
            raise RuntimeError("Fichier Ilian indisponible.")

        try:
            configuredParsedIlianModule = ast.parse(
                self.__configuredIlianPythonFile.read_text(encoding="utf-8"),
                filename=str(self.__configuredIlianPythonFile),
            )
        except (OSError, SyntaxError, UnicodeError) as error:
            raise RuntimeError("Fichier Ilian illisible ou invalide.") from error
        configuredMeanFunctionNode = next(
            (
                configuredNode
                for configuredNode in configuredParsedIlianModule.body
                if isinstance(configuredNode, ast.FunctionDef)
                and configuredNode.name == "moyenne"
            ),
            None,
        )
        if configuredMeanFunctionNode is None:
            raise RuntimeError("La fonction moyenne(lst, n) est introuvable.")

        configuredPositionalArgumentNames = [
            configuredArgument.arg
            for configuredArgument in configuredMeanFunctionNode.args.posonlyargs
            + configuredMeanFunctionNode.args.args
        ]
        if (
            configuredPositionalArgumentNames != ["lst", "n"]
            or configuredMeanFunctionNode.args.kwonlyargs
            or configuredMeanFunctionNode.args.vararg
            or configuredMeanFunctionNode.args.kwarg
        ):
            raise RuntimeError("La signature moyenne(lst, n) a change.")

        configuredMeanFunctionNode.decorator_list = []
        configuredMeanFunctionNode.returns = None
        configuredMeanFunctionNode.args.defaults = []
        configuredMeanFunctionNode.args.kw_defaults = [
            None for _ in configuredMeanFunctionNode.args.kwonlyargs
        ]
        for configuredArgument in (
            configuredMeanFunctionNode.args.posonlyargs
            + configuredMeanFunctionNode.args.args
            + configuredMeanFunctionNode.args.kwonlyargs
        ):
            configuredArgument.annotation = None

        configuredNamespace = {"__builtins__": {"range": range}}
        exec(
            compile(
                ast.fix_missing_locations(
                    ast.Module(
                        body=[configuredMeanFunctionNode],
                        type_ignores=[],
                    )
                ),
                str(self.__configuredIlianPythonFile),
                "exec",
            ),
            configuredNamespace,
        )
        return configuredNamespace["moyenne"]

    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        if len(configuredPopulationNumericDataTransferObject) == 0:
            return None

        if self.__configuredIlianMeanFunction is None:
            self.__configuredIlianMeanFunction = (
                self.__configuredLoadIlianMeanFunction()
            )

        return self.__configuredIlianMeanFunction(
            configuredPopulationNumericDataTransferObject,
            len(configuredPopulationNumericDataTransferObject),
        )


class DefaultConfiguredPopulationVarianceBeanImpl(
    IConfiguredAbstractPopulationVarianceBean
):
    def __init__(
        self,
        configuredMeanResolutionStrategyBean,
        configuredNormalizationBean,
    ):
        self.__configuredMeanResolutionStrategyBean = (
            configuredMeanResolutionStrategyBean
        )
        self.__configuredNormalizationBean = configuredNormalizationBean

    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        if len(configuredPopulationNumericDataTransferObject) == 0:
            return None

        configuredNormalizedPopulationNumericCollection = (
            self.__configuredNormalizationBean
            .configuredNormalizeJsonSerializableNumericPayload(
                configuredPopulationNumericDataTransferObject
            )
        )

        configuredResolvedPopulationArithmeticMeanValue = (
            self.__configuredMeanResolutionStrategyBean
            .configuredResolvePopulationMean(
                configuredNormalizedPopulationNumericCollection
            )
        )

        return (
            sum(
                map(
                    lambda configuredIndividualPopulationNumericObservation: (
                        configuredIndividualPopulationNumericObservation
                        - configuredResolvedPopulationArithmeticMeanValue
                    )
                    ** 2,
                    configuredNormalizedPopulationNumericCollection,
                )
            )
            / len(configuredNormalizedPopulationNumericCollection)
        )


class DelegatingConfiguredPopulationVarianceBeanProxy(
    IConfiguredAbstractPopulationVarianceBean
):
    def __init__(self, configuredDelegatePopulationVarianceBean):
        self.__configuredDelegatePopulationVarianceBean = (
            configuredDelegatePopulationVarianceBean
        )

    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        return (
            self.__configuredDelegatePopulationVarianceBean
            .configuredExecutePopulationStatisticalOperationBean(
                json.loads(
                    json.dumps(configuredPopulationNumericDataTransferObject)
                )
            )
        )


class DefaultConfiguredPopulationStandardDeviationBeanImpl(
    IConfiguredAbstractPopulationStandardDeviationBean
):
    def __init__(
        self,
        configuredPopulationVarianceBean,
        configuredNormalizationBean,
    ):
        self.__configuredPopulationVarianceBean = configuredPopulationVarianceBean
        self.__configuredNormalizationBean = configuredNormalizationBean

    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        configuredResolvedPopulationVarianceValue = (
            self.__configuredPopulationVarianceBean
            .configuredExecutePopulationStatisticalOperationBean(
                configuredPopulationNumericDataTransferObject
            )
        )

        if configuredResolvedPopulationVarianceValue is None:
            return None

        return math.sqrt(
            float(
                self.__configuredNormalizationBean
                .configuredNormalizeJsonSerializableNumericPayload(
                    configuredResolvedPopulationVarianceValue
                )
            )
        )


class ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager:
    @staticmethod
    def configuredGetJsonNormalizationBean():
        return DefaultConfiguredEnterpriseJsonNormalizationBeanImpl()

    @staticmethod
    def configuredGetPopulationMeanResolutionStrategyBean():
        return DefaultConfiguredPopulationMeanResolutionStrategyBeanImpl(
            ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
            .configuredGetJsonNormalizationBean()
        )

    @staticmethod
    def configuredGetPopulationVarianceBean():
        return DelegatingConfiguredPopulationVarianceBeanProxy(
            DefaultConfiguredPopulationVarianceBeanImpl(
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetPopulationMeanResolutionStrategyBean(),
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetJsonNormalizationBean(),
            )
        )

    @staticmethod
    def configuredGetPopulationMeanBean():
        return DefaultConfiguredPopulationMeanBeanImpl(
            ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
            .configuredGetPopulationMeanResolutionStrategyBean()
        )

    @staticmethod
    def configuredGetIlianPopulationMeanBean(configuredIlianPythonFile):
        return IlianConfiguredPopulationMeanBeanImpl(configuredIlianPythonFile)

    @staticmethod
    def configuredGetPopulationStandardDeviationBean():
        return DefaultConfiguredPopulationStandardDeviationBeanImpl(
            ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
            .configuredGetPopulationVarianceBean(),
            ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
            .configuredGetJsonNormalizationBean(),
        )


class ConfiguredPopulationStatisticsApplicationContextBean:
    def __init__(self):
        self.__configuredSingletonBeanRegistry = {
            "configuredPopulationVarianceBean": (
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetPopulationVarianceBean()
            ),
            "configuredPopulationMeanBean": (
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetPopulationMeanBean()
            ),
            "configuredIlianPopulationMeanBean": (
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetIlianPopulationMeanBean(
                    os.getenv("ILIAN_MOYENNE_FILE")
                )
            ),
            "configuredPopulationStandardDeviationBean": (
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetPopulationStandardDeviationBean()
            ),
        }

    def configuredGetBean(self, configuredEnterpriseBeanIdentifier):
        return self.__configuredSingletonBeanRegistry[
            configuredEnterpriseBeanIdentifier
        ]


__CONFIGURED_POPULATION_STATISTICS_APPLICATION_CONTEXT_BEAN = (
    ConfiguredPopulationStatisticsApplicationContextBean()
)


# ============================================================
# LES DEUX SEULES FONCTIONS PUBLIQUES DE CLEMENT — CDC §6
# ============================================================

def variance_population(nombres: list[float]) -> float | None:
    return (
        __CONFIGURED_POPULATION_STATISTICS_APPLICATION_CONTEXT_BEAN
        .configuredGetBean("configuredPopulationVarianceBean")
        .configuredExecutePopulationStatisticalOperationBean(nombres)
    )


def moyenne_population(
    nombres: list[float],
    utiliser_code_ilian: bool = False,
) -> float | None:
    configuredBeanIdentifier = (
        "configuredIlianPopulationMeanBean"
        if utiliser_code_ilian
        else "configuredPopulationMeanBean"
    )
    return (
        __CONFIGURED_POPULATION_STATISTICS_APPLICATION_CONTEXT_BEAN
        .configuredGetBean(configuredBeanIdentifier)
        .configuredExecutePopulationStatisticalOperationBean(nombres)
    )


def ecart_type(nombres: list[float]) -> float | None:
    configuredResolvedPopulationVarianceValue = variance_population(nombres)

    if configuredResolvedPopulationVarianceValue is None:
        return None

    return math.sqrt(configuredResolvedPopulationVarianceValue)
